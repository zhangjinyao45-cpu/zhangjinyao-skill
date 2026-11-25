#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coze 工作流 JSON 自检脚本 (coze_workflow_validator.py)

将 Phase 3.5 中可程序化的自检项固化为代码，
生成后一键运行即可发现结构性问题，提高自检稳定性。

用法:
    python coze_workflow_validator.py workflow.json

返回:
    每条规则的 PASS/FAIL/WARN 结果 + 修复建议
"""

import json
import sys
import re
from typing import Any
from collections import defaultdict

# ============================================================
# rawMeta.type 映射表 (自检项1核心)
# ============================================================
RAWMETA_MAP = {
    "string": 1, "integer": 2, "boolean": 3, "float": 4, "object": 6,
}
LIST_RAWMETA_MAP = {
    "string": 99, "integer": 100, "boolean": 101, "float": 102, "object": 103,
}
RAWMETA_REVERSE = {v: k for k, v in RAWMETA_MAP.items()}
RAWMETA_REVERSE.update({v: f"list[{k}]" for k, v in LIST_RAWMETA_MAP.items()})

# 节点高度表
NODE_HEIGHTS = {
    "3": 189.9, "4": 137.9, "5": 137.9, "6": 139.9, "8": 139.9,
    "9": 113.9, "12": 142.9, "15": 113.9, "18": 165.9, "21": 139.9,
    "22": 187.9, "27": 139.9, "28": 113.9, "30": 87.9, "32": 87.9,
    "40": 113.9, "42": 165.9, "43": 156.9, "44": 156.9, "45": 115.9,
    "46": 166.9, "58": 113.9,
}

# 节点类型 → subTitle 映射
NODE_SUBTITLE_MAP = {
    "3": "大模型", "4": "插件", "5": "代码", "6": "知识库检索",
    "8": "选择器", "9": "工作流调用", "12": "SQL自定义", "15": "文本处理",
    "18": "问答", "21": "循环", "22": "意图识别", "27": "知识库写入",
    "28": "批处理", "30": "输入", "32": "变量聚合", "40": "变量赋值",
    "42": "更新数据", "43": "查询数据", "44": "删除数据", "45": "HTTP请求",
    "46": "新增数据", "58": "JSON序列化",
}

# 需要 spaceId 的节点类型
SPACE_ID_REQUIRED_TYPES = {"4", "6", "12", "27", "42", "43", "44", "46"}


class ValidationResult:
    def __init__(self):
        self.results = []  # [(level, check_id, message)]

    def ok(self, check_id: str, msg: str):
        self.results.append(("PASS", check_id, msg))

    def fail(self, check_id: str, msg: str):
        self.results.append(("FAIL", check_id, msg))

    def warn(self, check_id: str, msg: str):
        self.results.append(("WARN", check_id, msg))

    def skip(self, check_id: str, msg: str):
        self.results.append(("SKIP", check_id, msg))

    def summary(self) -> str:
        lines = []
        lines.append("=" * 72)
        lines.append("  Coze 工作流 JSON 自检报告")
        lines.append("=" * 72)

        # Group by check_id
        by_check = defaultdict(list)
        for level, cid, msg in self.results:
            by_check[cid].append((level, msg))

        pass_count = sum(1 for l, _, _ in self.results if l == "PASS")
        fail_count = sum(1 for l, _, _ in self.results if l == "FAIL")
        warn_count = sum(1 for l, _, _ in self.results if l == "WARN")
        skip_count = sum(1 for l, _, _ in self.results if l == "SKIP")

        for level, cid, msg in self.results:
            icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}[level]
            lines.append(f"  {icon} [{level}] {cid}: {msg}")

        lines.append("")
        lines.append("-" * 72)
        lines.append(f"  总计: {pass_count} PASS / {fail_count} FAIL / {warn_count} WARN / {skip_count} SKIP")
        if fail_count == 0:
            lines.append("  🎉 所有可自动化检查项均通过!")
        else:
            lines.append(f"  🔴 有 {fail_count} 项致命问题需要修正!")
        lines.append("=" * 72)
        return "\n".join(lines)

    @property
    def has_failures(self) -> bool:
        return any(l == "FAIL" for l, _, _ in self.results)


def get_nodes(data: dict) -> list:
    """从剪贴板数据中提取节点列表"""
    return data.get("json", {}).get("nodes", [])


def get_edges(data: dict) -> list:
    """从剪贴板数据中提取顶层连线列表"""
    return data.get("json", {}).get("edges", [])


def node_desc(node: dict) -> str:
    """生成节点描述字符串"""
    nid = node.get("id", "?")
    title = node.get("data", {}).get("nodeMeta", {}).get("title", "?")
    ntype = node.get("type", "?")
    return f"节点 {nid}({title}, type={ntype})"


# ============================================================
# 自检项3: 代码节点 language=3
# ============================================================
def check_03_code_language(nodes: list, r: ValidationResult):
    code_nodes = [n for n in nodes if str(n.get("type")) == "5"]
    if not code_nodes:
        r.skip("自检项03", "无代码节点，跳过")
        return
    for n in code_nodes:
        lang = n.get("data", {}).get("inputs", {}).get("language")
        if lang == 3:
            r.ok("自检项03", f"{node_desc(n)} language=3 ✓")
        else:
            r.fail("自检项03", f"{node_desc(n)} language={lang}，应为 3")
        # 额外检查是否误用 codeLanguage
        if "codeLanguage" in n.get("data", {}).get("inputs", {}):
            r.fail("自检项03", f"{node_desc(n)} 含有非法字段 'codeLanguage'，应使用 'language': 3")


# ============================================================
# 自检项3.5: object输出子变量schema完整性
# ============================================================
def check_035_object_schema(nodes: list, r: ValidationResult):
    found = False
    # 数据库相关节点的 outputList schema 天然为空（粘贴后 GUI 配置），不算错误
    DB_TYPES = {"12", "42", "43", "44", "46"}
    for n in nodes:
        ntype = str(n.get("type", ""))
        outputs = n.get("data", {}).get("outputs", [])
        if not outputs:
            continue
        for out in outputs:
            otype = out.get("type")
            name = out.get("name", "?")

            # 跳过数据库节点的 outputList（schema 本身就是空的，用户在 GUI 选表后才填充）
            if ntype in DB_TYPES and name == "outputList":
                continue

            # object 类型
            if otype == "object":
                found = True
                schema = out.get("schema")
                if not schema or (isinstance(schema, list) and len(schema) == 0):
                    r.fail("自检项03.5", f"{node_desc(n)} 输出 '{name}' 类型为 object 但未定义 schema 子字段")
                elif isinstance(schema, dict) and schema.get("type") == "object" and not schema.get("schema"):
                    r.fail("自检项03.5", f"{node_desc(n)} 输出 '{name}' schema 只写了 type:object 但缺少子字段列表")
                else:
                    r.ok("自检项03.5", f"{node_desc(n)} 输出 '{name}' object schema 完整")
            # list[object] 类型
            if otype == "list":
                schema = out.get("schema", {})
                if isinstance(schema, dict) and schema.get("type") == "object":
                    found = True
                    sub = schema.get("schema")
                    if not sub or (isinstance(sub, list) and len(sub) == 0):
                        r.fail("自检项03.5", f"{node_desc(n)} 输出 '{name}' 类型为 list[object] 但内部 schema 未定义子字段")
                    else:
                        r.ok("自检项03.5", f"{node_desc(n)} 输出 '{name}' list[object] schema 完整")
    if not found:
        r.skip("自检项03.5", "无 object/list[object] 输出，跳过")


# ============================================================
# 自检项4: LLM 一致性
# ============================================================
def check_04_llm_consistency(nodes: list, r: ValidationResult):
    llm_nodes = [n for n in nodes if str(n.get("type")) == "3"]
    if not llm_nodes:
        r.skip("自检项04", "无 LLM 节点，跳过")
        return

    for n in llm_nodes:
        desc = node_desc(n)
        inputs = n.get("data", {}).get("inputs", {})
        llm_params = inputs.get("llmParam", [])
        param_dict = {}
        for p in llm_params:
            pname = p.get("name")
            pinput = p.get("input", {})
            pvalue = pinput.get("value", {})
            param_dict[pname] = pvalue

        # 4a: 模型三件套
        for field in ["modleName", "modelType", "generationDiversity"]:
            if field in param_dict:
                r.ok("自检项04", f"{desc} 模型字段 '{field}' 存在 ✓")
            else:
                r.fail("自检项04", f"{desc} 缺少必要模型字段 '{field}'")

        # 4b: 禁止字段
        if "modelName" in param_dict:
            r.fail("自检项04", f"{desc} 含有错误字段 'modelName'(应为 modleName)")
        for forbidden in ["frequencyPenalty", "presencePenalty"]:
            if forbidden in param_dict:
                r.fail("自检项04", f"{desc} 含有平台不支持的字段 '{forbidden}'")

        # 4c: thinking 字段
        if "thinking" in param_dict:
            r.ok("自检项04", f"{desc} thinking 字段存在 ✓")
        else:
            r.fail("自检项04", f"{desc} 缺少 thinking 字段")

        # 4d: prompt/systemPrompt 类型为 literal
        for pname in ["prompt", "systemPrompt"]:
            if pname in param_dict:
                vtype = param_dict[pname].get("type")
                if vtype == "literal":
                    r.ok("自检项04", f"{desc} {pname} 使用 literal ✓")
                else:
                    r.fail("自检项04", f"{desc} {pname} 类型为 '{vtype}'，必须为 'literal'")

        # 4e: responseFormat 值
        if "responseFormat" in param_dict:
            rf_val = param_dict["responseFormat"].get("content")
            if str(rf_val) in ("0", "1", "2"):
                r.ok("自检项04", f"{desc} responseFormat={rf_val} ✓")
            else:
                r.fail("自检项04", f"{desc} responseFormat={rf_val}，仅支持 0/1/2")

            # 4f: responseFormat=2 时检查 outputs 变量名
            if str(rf_val) == "2":
                outputs = n.get("data", {}).get("outputs", [])
                prompt_content = param_dict.get("prompt", {}).get("content", "")
                output_names = [o.get("name") for o in outputs
                               if o.get("name") not in ("reasoning_content", "errorBody", "isSuccess")]
                # 简单提示，不做深度 prompt 解析
                if output_names:
                    r.warn("自检项04", f"{desc} responseFormat=2，请确认 outputs {output_names} 与 Prompt 中 JSON 字段名一致")

        # 4g: version=3
        version = n.get("data", {}).get("version")
        if version == "3":
            r.ok("自检项04", f"{desc} data.version='3' ✓")
        else:
            r.fail("自检项04", f"{desc} data.version='{version}'，应为 '3'")


# ============================================================
# 自检项5: 容器节点结构
# ============================================================
def check_05_container_structure(nodes: list, r: ValidationResult):
    # 递归收集所有容器节点（包括嵌套的）
    def collect_containers(node_list):
        result = []
        for n in node_list:
            if str(n.get("type")) in ("21", "28"):
                result.append(n)
                result.extend(collect_containers(n.get("blocks", [])))
        return result

    container_nodes = collect_containers(nodes)
    if not container_nodes:
        r.skip("自检项05", "无容器节点(循环/批处理)，跳过")
        return

    for n in container_nodes:
        desc = node_desc(n)
        ntype = str(n.get("type"))

        # 5a: blocks/edges 在顶层
        if "blocks" in n:
            r.ok("自检项05", f"{desc} blocks 在节点顶层 ✓")
        else:
            # 检查是否误放在 data 内
            if "blocks" in n.get("data", {}):
                r.fail("自检项05", f"{desc} blocks 错误地放在 data 内部，应在节点顶层")
            else:
                r.fail("自检项05", f"{desc} 缺少 blocks 字段")

        if "edges" in n:
            r.ok("自检项05", f"{desc} edges 在节点顶层 ✓")
        else:
            if "edges" in n.get("data", {}):
                r.fail("自检项05", f"{desc} edges 错误地放在 data 内部，应在节点顶层")

        # 5b: outputs 使用 {name, input:{...}} 包装结构
        outputs = n.get("data", {}).get("outputs", [])
        for out in outputs:
            if "input" in out and "name" in out:
                r.ok("自检项05", f"{desc} 输出 '{out.get('name')}' 使用包装结构 ✓")
            elif "type" in out and "name" in out and "input" not in out:
                r.fail("自检项05", f"{desc} 输出 '{out.get('name')}' 使用了普通节点的扁平结构，容器节点必须用 {{name, input:{{type,schema,value}}}} 包装")

        # 5c: typed value 参数检查 (concurrentSize/batchSize/loopCount)
        inputs_data = n.get("data", {}).get("inputs", {})
        typed_params = ["concurrentSize", "batchSize", "loopCount"]
        for pname in typed_params:
            if pname in inputs_data:
                val = inputs_data[pname]
                if isinstance(val, dict) and "type" in val and "value" in val:
                    r.ok("自检项05", f"{desc} {pname} 使用 typed value 对象 ✓")
                elif isinstance(val, (int, float, str)):
                    r.fail("自检项05", f"{desc} {pname} 为裸数值 {val}，必须用 typed value 对象 {{type,value}}")


# ============================================================
# 自检项6: ref引用完整性
# ============================================================
def _check_refs_recursive(obj: Any, node_desc_str: str, r: ValidationResult, path: str = ""):
    """递归检查所有 ref 引用的 blockID 和 name 非空"""
    if isinstance(obj, dict):
        if obj.get("type") == "ref":
            content = obj.get("content", {})
            source = content.get("source", "")
            bid = content.get("blockID", "")
            name = content.get("name", "")
            # global_variable_app 不需要 blockID/name
            if source == "global_variable_app":
                return
            if not bid:
                r.fail("自检项06", f"{node_desc_str} {path}: ref 的 blockID 为空")
            if not name:
                r.fail("自检项06", f"{node_desc_str} {path}: ref 的 name 为空")
        for k, v in obj.items():
            _check_refs_recursive(v, node_desc_str, r, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _check_refs_recursive(v, node_desc_str, r, f"{path}[{i}]")


def check_06_ref_completeness(nodes: list, r: ValidationResult):
    found_ref = False
    for n in nodes:
        desc = node_desc(n)
        data = n.get("data", {})
        inputs = data.get("inputs", {})
        # 检查 inputParameters（兼容 left/right 结构）
        for ip in inputs.get("inputParameters", []):
            if not isinstance(ip, dict):
                continue
            _check_refs_recursive(ip, desc, r, "inputParameters")
            found_ref = True
        # 检查 branches (选择器)
        for br in inputs.get("branches", []):
            _check_refs_recursive(br, desc, r, "branches")
            found_ref = True
        # 检查 llmParam（兼容意图识别节点 llmParam 是 dict 的情况）
        llm_param = inputs.get("llmParam")
        if isinstance(llm_param, list):
            for lp in llm_param:
                if not isinstance(lp, dict):
                    continue
                if lp.get("name") in ("prompt", "systemPrompt"):
                    continue  # prompt 是 literal，不检查 ref
                _check_refs_recursive(lp, desc, r, "llmParam")
        elif isinstance(llm_param, dict):
            # 意图识别节点的 llmParam 是 object，跳过 ref 检查
            pass
        # 检查 mergeGroups (变量聚合)
        for mg in inputs.get("mergeGroups", []):
            if isinstance(mg, dict):
                _check_refs_recursive(mg, desc, r, "mergeGroups")
                found_ref = True
        # 检查 variableParameters（循环容器）
        for vp in inputs.get("variableParameters", []):
            if isinstance(vp, dict):
                _check_refs_recursive(vp, desc, r, "variableParameters")
                found_ref = True
    if not found_ref:
        r.skip("自检项06", "无 ref 引用，跳过")
    else:
        # 如果没有 fail，汇总一个 ok
        if not any(l == "FAIL" and c == "自检项06" for l, c, _ in r.results):
            r.ok("自检项06", "所有 ref 引用的 blockID/name 均非空 ✓")


# ============================================================
# 自检项7: 选择器条件结构
# ============================================================
def check_07_selector_structure(nodes: list, r: ValidationResult):
    selector_nodes = [n for n in nodes if str(n.get("type")) == "8"]
    if not selector_nodes:
        r.skip("自检项07", "无选择器节点，跳过")
        return

    UNARY_OPS = {9, 10, 11, 12}
    VALID_OPS = set(range(1, 17))

    for n in selector_nodes:
        desc = node_desc(n)
        branches = n.get("data", {}).get("inputs", {}).get("branches", [])
        if not branches:
            r.fail("自检项07", f"{desc} 未使用 branches 数组")
            continue

        for bi, branch in enumerate(branches):
            cond = branch.get("condition", {})
            conditions = cond.get("conditions", [])
            for ci, c in enumerate(conditions):
                op = c.get("operator")
                has_left = "left" in c
                has_right = "right" in c
                path = f"branch[{bi}].condition[{ci}]"

                if op not in VALID_OPS:
                    r.fail("自检项07", f"{desc} {path} operator={op} 超出有效范围 1~16")
                elif op in UNARY_OPS:
                    if has_right:
                        r.warn("自检项07", f"{desc} {path} 一元操作符(operator={op})不应有 right")
                    if not has_left:
                        r.fail("自检项07", f"{desc} {path} 缺少 left")
                else:
                    if not has_left:
                        r.fail("自检项07", f"{desc} {path} 缺少 left")
                    if not has_right:
                        r.fail("自检项07", f"{desc} {path} 二元操作符(operator={op})缺少 right")

                # 检查 left/right 的 {input:{...}} 包装
                if has_left:
                    left = c["left"]
                    if "input" not in left:
                        r.fail("自检项07", f"{desc} {path} left 缺少 {{'input':{{...}}}} 包装层")
                if has_right:
                    right = c["right"]
                    if "input" not in right:
                        r.fail("自检项07", f"{desc} {path} right 缺少 {{'input':{{...}}}} 包装层")

        if not any(l == "FAIL" and "自检项07" in c for l, c, _ in r.results):
            r.ok("自检项07", f"{desc} 选择器条件结构正确 ✓")


# ============================================================
# 自检项8: 变量聚合完整性
# ============================================================
def check_08_merge_completeness(nodes: list, r: ValidationResult):
    merge_nodes = [n for n in nodes if str(n.get("type")) == "32"]
    if not merge_nodes:
        r.skip("自检项08", "无变量聚合节点，跳过")
        return

    for n in merge_nodes:
        desc = node_desc(n)
        inputs = n.get("data", {}).get("inputs", {})
        outputs = n.get("data", {}).get("outputs", [])
        merge_groups = inputs.get("mergeGroups", [])

        if not outputs:
            r.fail("自检项08", f"{desc} outputs 为空数组")
        if not merge_groups:
            r.fail("自检项08", f"{desc} mergeGroups 为空")
            continue

        for gi, mg in enumerate(merge_groups):
            gname = mg.get("name", "")
            if len(gname) > 20:
                r.fail("自检项08", f"{desc} mergeGroups[{gi}].name='{gname}' 超过20字符")
            variables = mg.get("variables", [])
            if not variables:
                r.fail("自检项08", f"{desc} mergeGroups[{gi}].variables 为空")
            for vi, v in enumerate(variables):
                # 变量聚合 variables 的实际结构: {type, value: {type:"ref", content: {source, blockID, name}}}
                content = v.get("value", {}).get("content", {}) if isinstance(v.get("value"), dict) else {}
                bid = content.get("blockID", "") or v.get("blockID", "")
                vname = content.get("name", "") or v.get("name", "")
                if not bid or not vname:
                    r.fail("自检项08", f"{desc} mergeGroups[{gi}].variables[{vi}] blockID 或 name 为空")

        # 检查 mergeGroups.name 与 outputs.name 对应
        mg_names = {mg.get("name") for mg in merge_groups}
        out_names = {o.get("name") for o in outputs}
        if mg_names != out_names:
            r.fail("自检项08", f"{desc} mergeGroups names {mg_names} 与 outputs names {out_names} 不匹配")
        else:
            r.ok("自检项08", f"{desc} 变量聚合结构完整 ✓")


# ============================================================
# 自检项9: processType=2 完整性
# ============================================================
def check_09_process_type_2(nodes: list, r: ValidationResult):
    found = False
    for n in nodes:
        desc = node_desc(n)
        ntype = str(n.get("type"))
        inputs = n.get("data", {}).get("inputs", {})
        soe = inputs.get("settingOnError", {})
        if soe.get("processType") != 2:
            continue
        found = True

        # switch: true
        if soe.get("switch") is True:
            r.ok("自检项09", f"{desc} settingOnError.switch=true ✓")
        else:
            r.fail("自检项09", f"{desc} processType=2 但缺少 switch:true")

        # dataOnErr
        if "dataOnErr" in soe and soe["dataOnErr"]:
            r.ok("自检项09", f"{desc} dataOnErr 存在 ✓")
        else:
            r.fail("自检项09", f"{desc} processType=2 但缺少 dataOnErr")

        # outputs 中的 errorBody 和 isSuccess
        outputs = n.get("data", {}).get("outputs", [])
        out_names = [o.get("name") for o in outputs]
        if "errorBody" in out_names:
            r.ok("自检项09", f"{desc} outputs 包含 errorBody ✓")
        else:
            r.fail("自检项09", f"{desc} processType=2 但 outputs 缺少 errorBody")
        if "isSuccess" in out_names:
            r.ok("自检项09", f"{desc} outputs 包含 isSuccess ✓")
        else:
            r.fail("自检项09", f"{desc} processType=2 但 outputs 缺少 isSuccess")

        # LLM 额外: dataOnErr 含 reasoning_content, backupLLmParam
        if ntype == "3":
            doe = soe.get("dataOnErr", "")
            if "reasoning_content" not in doe:
                r.fail("自检项09", f"{desc} LLM 节点 dataOnErr 缺少 reasoning_content")
            retry = soe.get("retryTimes", 0)
            if retry and retry >= 1:
                ext = soe.get("ext", {})
                backup = ext.get("backupLLmParam", "")
                if backup:
                    if "modleName" in backup:
                        r.ok("自检项09", f"{desc} backupLLmParam 使用 modleName ✓")
                    if "modelName" in backup and "modleName" not in backup:
                        r.fail("自检项09", f"{desc} backupLLmParam 中用了 modelName，应为 modleName")
                else:
                    r.fail("自检项09", f"{desc} retryTimes≥1 但缺少 backupLLmParam")

    if not found:
        r.skip("自检项09", "无 processType=2 节点，跳过")


# ============================================================
# 自检项10 (部分): 代码节点代码质量 - f-string反斜杠 + unicode
# ============================================================
def check_10_code_quality(nodes: list, r: ValidationResult):
    code_nodes = [n for n in nodes if str(n.get("type")) == "5"]
    if not code_nodes:
        r.skip("自检项10", "无代码节点，跳过")
        return

    for n in code_nodes:
        desc = node_desc(n)
        code = n.get("data", {}).get("inputs", {}).get("code", "")
        if not code:
            r.warn("自检项10", f"{desc} code 为空")
            continue

        # f-string 中的反斜杠检查 (粗略匹配)
        # 匹配 f"...{...含反斜杠...}..."
        fstring_backslash = re.findall(r'''f['"](.*?\{[^}]*\\[^}]*\}.*?)['"']''', code)
        if fstring_backslash:
            r.fail("自检项10", f"{desc} f-string 中可能含有反斜杠: {fstring_backslash[:2]}")
        else:
            r.ok("自检项10", f"{desc} f-string 无反斜杠问题 ✓")

        # unicode 编码检查
        unicode_matches = re.findall(r'\\u[0-9a-fA-F]{4}', code)
        if unicode_matches:
            r.fail("自检项10", f"{desc} 代码中含有 unicode 编码: {unicode_matches[:3]}...，应直接写中文")
        else:
            r.ok("自检项10", f"{desc} 无 unicode 编码问题 ✓")

        # Object-First: 检查是否有 json.dumps(dict) 然后 append 的反模式
        if re.search(r'json\.dumps\s*\(', code) and re.search(r'\.append\s*\(', code):
            r.warn("自检项10", f"{desc} 检测到 json.dumps + append 模式，请确认是否违反 Object-First 原则")


# ============================================================
# 自检项10b: 批处理输出结构
# ============================================================
def check_10b_batch_output(nodes: list, r: ValidationResult):
    batch_nodes = [n for n in nodes if str(n.get("type")) == "28"]
    if not batch_nodes:
        r.skip("自检项10b", "无批处理节点，跳过")
        return

    for n in batch_nodes:
        desc = node_desc(n)
        outputs = n.get("data", {}).get("outputs", [])

        # 检查每个输出是否是独立的 list
        for out in outputs:
            out_name = out.get("name", "?")
            out_input = out.get("input", {})
            if out_input.get("type") == "list":
                r.ok("自检项10b", f"{desc} 输出 '{out_name}' 类型为 list ✓")
            elif out_input.get("type") == "object" or (isinstance(out_input, dict) and out_input.get("schema", {}).get("type") == "object"):
                r.fail("自检项10b", f"{desc} 输出 '{out_name}' 不应为单个 object，批处理输出应为独立的 list 变量")


# ============================================================
# 自检项11: HTTP节点变量引用方式
# ============================================================
def check_11_http_node(nodes: list, r: ValidationResult):
    http_nodes = [n for n in nodes if str(n.get("type")) == "45"]
    if not http_nodes:
        r.skip("自检项11", "无 HTTP 节点，跳过")
        return

    for n in http_nodes:
        desc = node_desc(n)
        data = n.get("data", {})
        inputs = data.get("inputs", {})

        # 11a: inputParameters 位置
        if "inputParameters" in data:
            r.ok("自检项11", f"{desc} inputParameters 在 data 层 ✓")
        if "inputParameters" in inputs:
            r.fail("自检项11", f"{desc} inputParameters 错误地放在 data.inputs 内，应在 data 层（与 inputs 平级）")

        # 11b: url/json/rawText 中不应有 {{varName}} 格式（应该是 {{block_output_ID.name}}）
        for field in ["url"]:
            val = inputs.get(field, {})
            if isinstance(val, dict):
                content = val.get("value", {}).get("content", "")
            elif isinstance(val, str):
                content = val
            else:
                continue
            # 检查是否用了简单变量名（非 block_output_ 开头）
            simple_refs = re.findall(r'\{\{(?!block_output_|global_variable_)(\w+)\}\}', str(content))
            if simple_refs:
                r.warn("自检项11", f"{desc} url 中引用 {simple_refs} 不是 {{{{block_output_ID.name}}}} 格式")

        # 11c: bodyType 合法性
        body_data = inputs.get("bodyData", {})
        body_type = body_data.get("bodyType", "")
        valid_body_types = {"JSON", "FORM_DATA", "FORM_URLENCODED", "RAW_TEXT", "BINARY", "EMPTY"}
        if body_type and body_type not in valid_body_types:
            r.fail("自检项11", f"{desc} bodyType='{body_type}' 不合法，有效值: {valid_body_types}")
        elif body_type:
            r.ok("自检项11", f"{desc} bodyType='{body_type}' ✓")


# ============================================================
# 自检项12: 资源类节点 spaceId
# ============================================================
def check_12_space_id(data: dict, nodes: list, r: ValidationResult):
    resource_nodes = [n for n in nodes if str(n.get("type")) in SPACE_ID_REQUIRED_TYPES]
    if not resource_nodes:
        r.skip("自检项12", "无资源类节点，跳过")
        return

    space_id = data.get("source", {}).get("spaceId", "")
    if not space_id:
        r.fail("自检项12", "工作流包含资源类节点但顶层 source.spaceId 为空")
    elif space_id in ("placeholder", "your_space_id", "{{SPACE_ID}}"):
        r.fail("自检项12", f"source.spaceId 为占位符 '{space_id}'，必须填真实值")
    else:
        r.ok("自检项12", f"source.spaceId='{space_id}' ✓")

    # 检查 databaseInfoList / datasetList
    for n in resource_nodes:
        desc = node_desc(n)
        inputs = n.get("data", {}).get("inputs", {})
        for list_name in ["databaseInfoList", "datasetList"]:
            if list_name in inputs:
                val = inputs[list_name]
                if isinstance(val, list) and len(val) == 0:
                    r.ok("自检项12", f"{desc} {list_name} 为空数组（用户需在 GUI 中选择）✓")
                elif isinstance(val, list) and len(val) > 0:
                    # 检查是否为正确格式: [{"databaseInfoID": "..."}] 或 [{"datasetID": "..."}]
                    first = val[0] if val else {}
                    if list_name == "databaseInfoList" and isinstance(first, dict):
                        if "databaseInfoID" in first:
                            did = first["databaseInfoID"]
                            if did and not did.startswith("{{"):
                                r.ok("自检项12", f"{desc} {list_name} 已预填 databaseInfoID='{did}' ✓")
                            else:
                                r.warn("自检项12", f"{desc} {list_name} databaseInfoID 为占位符 '{did}'，确认用户已提供真实值")
                        else:
                            r.fail("自检项12", f"{desc} {list_name} 格式错误: 缺少 databaseInfoID 字段，正确格式为 [{{'databaseInfoID': '...'}}]")
                    else:
                        r.ok("自检项12", f"{desc} {list_name} 已预填(len={len(val)}) ✓")


# ============================================================
# 自检项13: SQL自定义变量引用
# ============================================================
def check_13_sql_variables(nodes: list, r: ValidationResult):
    sql_nodes = [n for n in nodes if str(n.get("type")) == "12"]
    if not sql_nodes:
        r.skip("自检项13", "无 SQL 自定义节点，跳过")
        return

    for n in sql_nodes:
        desc = node_desc(n)
        inputs = n.get("data", {}).get("inputs", {})
        sql = inputs.get("sql", "")
        ip_names = {p.get("name") for p in inputs.get("inputParameters", [])}

        # 提取 SQL 中的 {{变量名}} （支持 block_output_ID.name 格式）
        sql_vars_raw = set(re.findall(r'\{\{([\w.]+)\}\}', sql))

        # 检查是否有 block_output_ 格式的直接引用
        direct_refs = [v for v in sql_vars_raw if v.startswith("block_output_")]
        if direct_refs:
            r.fail("自检项13", f"{desc} SQL 中直接引用了上游 blockID: {direct_refs}，应通过 inputParameters 声明变量")

        # 仅保留纯变量名（非 block_output_ 开头的）做声明检查
        sql_vars = {v for v in sql_vars_raw if not v.startswith("block_output_")}

        # 检查变量是否在 inputParameters 中声明
        undeclared = sql_vars - ip_names
        if undeclared:
            r.fail("自检项13", f"{desc} SQL 中引用了未在 inputParameters 中声明的变量: {undeclared}")
        else:
            r.ok("自检项13", f"{desc} SQL 变量引用正确 ✓")

        # INSERT 语句 uuid 检查
        if re.search(r'\bINSERT\b', sql, re.IGNORECASE):
            if re.search(r'\buuid\b', sql, re.IGNORECASE):
                r.ok("自检项13", f"{desc} INSERT 包含 uuid 列 ✓")
            else:
                r.fail("自检项13", f"{desc} INSERT 缺少 uuid 列")


# ============================================================
# 自检项13b: 查询/SQL rowNum 陷阱
# ============================================================
def check_13b_rownum_trap(nodes: list, edges: list, r: ValidationResult):
    """检查是否有选择器节点判断了查询数据/SQL自定义节点的 rowNum"""
    query_nodes = {n["id"] for n in nodes if str(n.get("type")) in ("43", "12")}
    if not query_nodes:
        r.skip("自检项13b", "无查询数据/SQL自定义节点，跳过")
        return

    selector_nodes = [n for n in nodes if str(n.get("type")) == "8"]
    for sn in selector_nodes:
        desc = node_desc(sn)
        branches = sn.get("data", {}).get("inputs", {}).get("branches", [])
        for br in branches:
            conditions = br.get("condition", {}).get("conditions", [])
            for cond in conditions:
                left = cond.get("left", {}).get("input", {}).get("value", {}).get("content", {})
                if isinstance(left, dict):
                    bid = left.get("blockID", "")
                    name = left.get("name", "")
                    if bid in query_nodes and name == "rowNum":
                        r.fail("自检项13b", f"{desc} 判断了查询数据/SQL自定义节点({bid})的 rowNum，该值始终为 null！应判断 outputList 是否为空")

    if not any(l == "FAIL" and "自检项13b" in c for l, c, _ in r.results):
        r.ok("自检项13b", "未发现 rowNum 陷阱 ✓")


# ============================================================
# 自检项13c: 数据库节点变量与字段一一对应
# ============================================================
def check_13c_db_field_mapping(nodes: list, r: ValidationResult):
    db_types = {"42", "43", "44", "46"}
    db_nodes = [n for n in nodes if str(n.get("type")) in db_types]
    if not db_nodes:
        r.skip("自检项13c", "无数据库节点，跳过")
        return

    for n in db_nodes:
        desc = node_desc(n)
        ntype = str(n.get("type"))
        inputs = n.get("data", {}).get("inputs", {})

        # 检查 databaseInfoList 格式
        dil = inputs.get("databaseInfoList", [])
        if isinstance(dil, list) and len(dil) > 0:
            for di in dil:
                if isinstance(di, dict) and "databaseInfoID" not in di:
                    r.fail("自检项13c", f"{desc} databaseInfoList 格式错误: 缺少 databaseInfoID 字段，正确格式为 [{{'databaseInfoID': '...'}}]")

        # 检查 fieldInfo 中 fieldID 是否为数字字符串（新增/更新节点）
        if ntype in ("42", "46"):
            param_key = "updateParam" if ntype == "42" else "insertParam"
            param = inputs.get(param_key, {})
            field_info = param.get("fieldInfo", [])
            for fi_idx, fi_pair in enumerate(field_info):
                if not isinstance(fi_pair, list):
                    continue
                for item in fi_pair:
                    if isinstance(item, dict) and item.get("name") == "fieldID":
                        fid_val = item.get("input", {}).get("value", {})
                        content = fid_val.get("content", "")
                        if content and not content.startswith("{{"):
                            # 应该是数字字符串或纯数字
                            if not content.isdigit():
                                r.fail("自检项13c", f"{desc} fieldInfo[{fi_idx}] fieldID='{content}' 不是数字字符串，应为字段编号如 '1','2','3'")
                            else:
                                r.ok("自检项13c", f"{desc} fieldInfo[{fi_idx}] fieldID='{content}' 格式正确 ✓")

        # 检查 conditionList 中 left 字段名非空
        for param_key in ("updateParam", "selectParam", "deleteParam"):
            param = inputs.get(param_key, {})
            condition = param.get("condition", {})
            cond_list = condition.get("conditionList", [])
            for ci, cond_triple in enumerate(cond_list):
                if not isinstance(cond_triple, list):
                    continue
                for item in cond_triple:
                    if isinstance(item, dict) and item.get("name") == "left":
                        left_content = item.get("input", {}).get("value", {}).get("content", "")
                        if not left_content:
                            r.fail("自检项13c", f"{desc} conditionList[{ci}].left 字段名为空")

    if not any(l == "FAIL" and "自检项13c" in c for l, c, _ in r.results):
        r.ok("自检项13c", "数据库节点字段映射检查通过 ✓")


# ============================================================
# 自检项14b: 连线格式完整性
# ============================================================
def check_14b_edge_format(data: dict, nodes: list, r: ValidationResult):
    edges = get_edges(data)
    node_ids = {n["id"] for n in nodes}

    if not edges:
        r.warn("自检项14b", "顶层无连线 edges（可能全部在容器内部）")
        return

    for i, e in enumerate(edges):
        required = ["sourceNodeID", "targetNodeID", "sourcePortID", "targetPortID"]
        missing = [f for f in required if f not in e]
        if missing:
            r.fail("自检项14b", f"edges[{i}] 缺少字段: {missing}")
            continue

        src = e["sourceNodeID"]
        tgt = e["targetNodeID"]
        # 检查节点 ID 是否存在 (开始节点100001/结束节点900001可能不在 nodes 中)
        if src not in node_ids and src not in ("100001", "100002", "900001"):
            r.warn("自检项14b", f"edges[{i}] sourceNodeID='{src}' 不在 nodes 中")
        if tgt not in node_ids and tgt not in ("100001", "100002", "900001"):
            r.warn("自检项14b", f"edges[{i}] targetNodeID='{tgt}' 不在 nodes 中")

        # 选择器端口检查
        sport = e.get("sourcePortID", "")
        if sport and not re.match(r'^(true(_\d+)?|false|branch_error|batch-function-inline-output|loop-function-inline-output|)$', sport):
            # 检查是否误用了 branch-0 等格式
            if re.match(r'^branch-\d+$', sport):
                r.fail("自检项14b", f"edges[{i}] sourcePortID='{sport}' 格式错误，应使用 true/true_1/false")

    if not any(l == "FAIL" and "自检项14b" in c for l, c, _ in r.results):
        r.ok("自检项14b", "连线格式完整 ✓")

    # 检查开始/结束节点连线
    start_edges = [e for e in edges if e.get("sourceNodeID") == "100001"]
    end_edges = [e for e in edges if e.get("targetNodeID") == "900001"]
    if start_edges:
        r.ok("自检项14b", f"开始节点(100001)已有 {len(start_edges)} 条出边 ✓")
    else:
        r.warn("自检项14b", "未发现从开始节点(100001)出发的连线，粘贴后需手动连接开始节点")
    if end_edges:
        r.ok("自检项14b", f"结束节点(900001)已有 {len(end_edges)} 条入边 ✓")
    else:
        r.warn("自检项14b", "未发现连向结束节点(900001)的连线，粘贴后需手动连接结束节点")


# ============================================================
# 自检项15: externalData.title 校验
# ============================================================
def check_15_external_data_title(nodes: list, r: ValidationResult):
    for n in nodes:
        desc = node_desc(n)
        ntype = str(n.get("type"))
        temp = n.get("_temp", {})
        ext = temp.get("externalData", {})
        ext_title = ext.get("title", "")
        expected = NODE_SUBTITLE_MAP.get(ntype)
        node_meta = n.get("data", {}).get("nodeMeta", {})
        sub_title = node_meta.get("subTitle", "")

        if not temp:
            r.fail("自检项15", f"{desc} 缺少 _temp 字段")
            continue

        if not ext:
            r.fail("自检项15", f"{desc} 缺少 _temp.externalData")
            continue

        if expected and ext_title != expected:
            user_title = node_meta.get("title", "")
            if ext_title == user_title and ext_title != expected:
                r.fail("自检项15", f"{desc} externalData.title='{ext_title}' 错误地填了用户自定义 title，应为 subTitle: '{expected}'")
            elif ext_title != expected:
                r.warn("自检项15", f"{desc} externalData.title='{ext_title}'，期望 '{expected}'")
        elif expected:
            r.ok("自检项15", f"{desc} externalData.title='{ext_title}' ✓")


# ============================================================
# 自检项16: 意图识别节点差异
# ============================================================
def check_16_intent_node(nodes: list, r: ValidationResult):
    intent_nodes = [n for n in nodes if str(n.get("type")) == "22"]
    if not intent_nodes:
        r.skip("自检项16", "无意图识别节点，跳过")
        return

    for n in intent_nodes:
        desc = node_desc(n)
        inputs = n.get("data", {}).get("inputs", {})
        llm_param = inputs.get("llmParam")

        # llmParam 应为 object 不是 array
        if isinstance(llm_param, list):
            r.fail("自检项16", f"{desc} llmParam 是 array，意图识别节点应为 object")
        elif isinstance(llm_param, dict):
            r.ok("自检项16", f"{desc} llmParam 是 object ✓")

            # 模型字段应为 modelName 不是 modleName
            if "modelName" in llm_param:
                r.ok("自检项16", f"{desc} 使用 modelName（意图识别节点正确） ✓")
            if "modleName" in llm_param:
                r.fail("自检项16", f"{desc} 使用了 modleName，意图识别节点应用 modelName")


# ============================================================
# 自检项17: 选择器 branches 结构 + 端口命名
# ============================================================
def check_17_selector_ports(nodes: list, edges: list, r: ValidationResult):
    selector_nodes = [n for n in nodes if str(n.get("type")) == "8"]
    if not selector_nodes:
        r.skip("自检项17", "无选择器节点，跳过")
        return

    # 收集所有层级的 edges（包括容器内部 edges）
    all_edges = list(edges)
    for n in nodes:
        if str(n.get("type")) in ("21", "28"):
            all_edges.extend(n.get("edges", []))

    for n in selector_nodes:
        desc = node_desc(n)
        nid = n.get("id")
        branches = n.get("data", {}).get("inputs", {}).get("branches", [])

        if not branches:
            r.fail("自检项17", f"{desc} 未使用 branches 数组")
            continue

        r.ok("自检项17", f"{desc} 使用 branches 数组(len={len(branches)}) ✓")

        # 检查连线端口命名
        node_edges = [e for e in all_edges if e.get("sourceNodeID") == nid]
        ports = {e.get("sourcePortID") for e in node_edges}

        # 期望端口: true, true_1, ..., true_{N-1}, false
        expected_ports = {"true", "false"}
        for i in range(1, len(branches)):
            expected_ports.add(f"true_{i}")

        bad_ports = ports - expected_ports - {"", "branch_error"}
        if bad_ports:
            r.fail("自检项17", f"{desc} 端口命名错误: {bad_ports}，期望: {expected_ports}")
        elif ports:
            r.ok("自检项17", f"{desc} 端口命名正确 ✓")


# ============================================================
# 自检项18: processType=3 异常端口
# ============================================================
def check_18_error_branch(nodes: list, edges: list, r: ValidationResult):
    # 收集所有层级的 edges
    all_edges = list(edges)
    for n in nodes:
        if str(n.get("type")) in ("21", "28"):
            all_edges.extend(n.get("edges", []))

    found = False
    for n in nodes:
        soe = n.get("data", {}).get("inputs", {}).get("settingOnError", {})
        if soe.get("processType") != 3:
            continue
        found = True
        desc = node_desc(n)
        nid = n.get("id")

        error_edges = [e for e in all_edges if e.get("sourceNodeID") == nid and e.get("sourcePortID") == "branch_error"]
        if error_edges:
            r.ok("自检项18", f"{desc} processType=3 有 branch_error 连线 ✓")
        else:
            r.fail("自检项18", f"{desc} processType=3 但缺少 sourcePortID='branch_error' 的连线")

    if not found:
        r.skip("自检项18", "无 processType=3 节点，跳过")


# ============================================================
# 自检项19: 设置变量 left/right 结构
# ============================================================
def check_19_set_variable(nodes: list, r: ValidationResult):
    # 从容器节点内部查找 type=20
    set_var_nodes = []
    for n in nodes:
        if str(n.get("type")) in ("21", "28"):
            for block in n.get("blocks", []):
                if str(block.get("type")) == "20":
                    set_var_nodes.append(block)
    # 也检查顶层
    for n in nodes:
        if str(n.get("type")) == "20":
            set_var_nodes.append(n)

    if not set_var_nodes:
        r.skip("自检项19", "无设置变量节点，跳过")
        return

    for n in set_var_nodes:
        desc = node_desc(n)
        ips = n.get("data", {}).get("inputs", {}).get("inputParameters", [])
        for ip in ips:
            if "left" in ip and "right" in ip:
                r.ok("自检项19", f"{desc} 使用 left/right 赋值结构 ✓")
            elif "name" in ip and "input" in ip and "left" not in ip:
                r.fail("自检项19", f"{desc} 使用了 name/input 结构，设置变量节点应使用 left/right 赋值结构")


# ============================================================
# 自检项20: 知识库检索参数名
# ============================================================
def check_20_kb_query_param(nodes: list, r: ValidationResult):
    kb_nodes = [n for n in nodes if str(n.get("type")) == "6"]
    if not kb_nodes:
        r.skip("自检项20", "无知识库检索节点，跳过")
        return

    for n in kb_nodes:
        desc = node_desc(n)
        ips = n.get("data", {}).get("inputs", {}).get("inputParameters", [])
        ip_names = [p.get("name") for p in ips]

        if "Query" in ip_names:
            r.ok("自检项20", f"{desc} inputParameters 参数名为 'Query'(大写Q) ✓")
        elif "query" in ip_names:
            r.fail("自检项20", f"{desc} 参数名为 'query'(小写q)，应为 'Query'(大写Q)")
        else:
            r.fail("自检项20", f"{desc} inputParameters 缺少 'Query' 参数")

        # outputs 固定检查
        outputs = n.get("data", {}).get("outputs", [])
        out_names = [o.get("name") for o in outputs]
        if "outputList" in out_names:
            r.ok("自检项20", f"{desc} outputs 包含 outputList ✓")
        else:
            r.fail("自检项20", f"{desc} outputs 缺少固定输出 outputList")


# ============================================================
# 自检项21: 知识库写入完整性
# ============================================================
def check_21_kb_write(nodes: list, r: ValidationResult):
    kb_write_nodes = [n for n in nodes if str(n.get("type")) == "27"]
    if not kb_write_nodes:
        r.skip("自检项21", "无知识库写入节点，跳过")
        return

    for n in kb_write_nodes:
        desc = node_desc(n)
        inputs = n.get("data", {}).get("inputs", {})

        # inputParameters 应为空
        ips = inputs.get("inputParameters", [])
        if len(ips) == 0:
            r.ok("自检项21", f"{desc} inputParameters 为空 ✓")
        else:
            r.fail("自检项21", f"{desc} inputParameters 应为空数组")

        # strategyParam 三个策略
        sp = inputs.get("strategyParam", {})
        for strategy in ["parsingStrategy", "chunkStrategy", "indexStrategy"]:
            if strategy in sp:
                r.ok("自检项21", f"{desc} strategyParam 包含 {strategy} ✓")
            else:
                r.fail("自检项21", f"{desc} strategyParam 缺少 {strategy}")


# ============================================================
# 自检项1 (部分): rawMeta.type 精确匹配
# ============================================================
def check_01_rawmeta_mapping(nodes: list, r: ValidationResult):
    """检查所有 rawMeta.type 是否与声明的 type 匹配"""
    errors = []

    def check_value_rawmeta(val_obj: dict, context: str):
        if not isinstance(val_obj, dict):
            return
        vtype = val_obj.get("type")
        # 检查 value 内的 rawMeta
        value = val_obj.get("value", {})
        if isinstance(value, dict):
            raw_meta = value.get("rawMeta", {})
            if raw_meta and "type" in raw_meta:
                rm_type = raw_meta["type"]

                # 标量类型检查
                expected = RAWMETA_MAP.get(vtype)
                if expected and rm_type != expected:
                    errors.append(f"{context}: type='{vtype}' 但 rawMeta.type={rm_type}，应为 {expected}")
                    return

                # list 类型检查：rawMeta 应对应 LIST_RAWMETA_MAP[schema.type]
                if vtype == "list":
                    schema = val_obj.get("schema", {})
                    schema_type = schema.get("type") if isinstance(schema, dict) else None
                    if schema_type:
                        expected_list = LIST_RAWMETA_MAP.get(schema_type)
                        if expected_list and rm_type != expected_list:
                            errors.append(f"{context}: type='list', schema.type='{schema_type}' 但 rawMeta.type={rm_type}，应为 {expected_list} (list[{schema_type}])")
                    elif rm_type not in LIST_RAWMETA_MAP.values():
                        errors.append(f"{context}: type='list' 但 rawMeta.type={rm_type} 不在 list 类型映射范围内(99~103)")

    for n in nodes:
        desc = node_desc(n)
        inputs = n.get("data", {}).get("inputs", {})

        # 检查 inputParameters（兼容 left/right 结构的设置变量节点）
        for ip in inputs.get("inputParameters", []):
            if not isinstance(ip, dict):
                continue
            # 标准 name/input 结构
            inp = ip.get("input", {})
            if isinstance(inp, dict):
                check_value_rawmeta(inp, f"{desc}.inputParameters.{ip.get('name', '?')}")
            # left/right 结构（设置变量节点）
            for side in ("left", "right"):
                side_val = ip.get(side)
                if isinstance(side_val, dict):
                    check_value_rawmeta(side_val, f"{desc}.inputParameters.{side}")

        # 检查 llmParam（注意：意图识别节点的 llmParam 是 object 而非 array）
        llm_param = inputs.get("llmParam")
        if isinstance(llm_param, list):
            for lp in llm_param:
                if not isinstance(lp, dict):
                    continue
                inp = lp.get("input", {})
                if isinstance(inp, dict):
                    check_value_rawmeta(inp, f"{desc}.llmParam.{lp.get('name', '?')}")
        # 意图识别节点 llmParam 是 dict，跳过（其内部结构不同）

    if errors:
        for e in errors:
            r.fail("自检项01", e)
    else:
        r.ok("自检项01", "rawMeta.type 映射检查通过 ✓")


# ============================================================
# 自检项22: 循环全链路 schema 一致性 (部分)
# ============================================================
def check_22_loop_schema(nodes: list, r: ValidationResult):
    loop_nodes = [n for n in nodes if str(n.get("type")) == "21"]
    if not loop_nodes:
        r.skip("自检项22", "无循环节点，跳过")
        return

    for n in loop_nodes:
        desc = node_desc(n)
        inputs = n.get("data", {}).get("inputs", {})
        var_params = inputs.get("variableParameters", [])

        # 检查 variableParameters 的 schema 是否定义
        for vp in var_params:
            vpname = vp.get("name", "?")
            vp_input = vp.get("input", {})
            vp_schema = vp_input.get("schema", {})
            if vp_input.get("type") == "object" and (not vp_schema or vp_schema == {}):
                r.warn("自检项22", f"{desc} variableParameter '{vpname}' type=object 但 schema 为空，需与上游一致")
            elif vp_input.get("type") == "list" and (not vp_schema or vp_schema == {}):
                r.warn("自检项22", f"{desc} variableParameter '{vpname}' type=list 但 schema 为空")
            else:
                r.ok("自检项22", f"{desc} variableParameter '{vpname}' schema 存在 ✓")


# ============================================================
# 主函数
# ============================================================
def validate_workflow(data: dict) -> ValidationResult:
    r = ValidationResult()
    nodes = get_nodes(data)
    edges = get_edges(data)

    # 收集容器内部节点一并检查
    all_nodes = list(nodes)
    for n in nodes:
        if str(n.get("type")) in ("21", "28"):
            all_nodes.extend(n.get("blocks", []))

    if not nodes:
        r.fail("GLOBAL", "未找到任何节点 (json.nodes 为空)")
        return r

    # 顶层结构检查
    if data.get("type") != "coze-workflow-clipboard-data":
        r.fail("GLOBAL", f"顶层 type='{data.get('type')}'，应为 'coze-workflow-clipboard-data'")
    else:
        r.ok("GLOBAL", "顶层 type 正确 ✓")

    # 按自检项逐项执行
    check_01_rawmeta_mapping(all_nodes, r)
    check_03_code_language(all_nodes, r)
    check_035_object_schema(all_nodes, r)
    check_04_llm_consistency(all_nodes, r)
    check_05_container_structure(nodes, r)  # 容器结构: 检查顶层 + 嵌套容器
    check_06_ref_completeness(all_nodes, r)
    check_07_selector_structure(all_nodes, r)
    check_08_merge_completeness(all_nodes, r)
    check_09_process_type_2(all_nodes, r)
    check_10_code_quality(all_nodes, r)
    check_10b_batch_output(nodes, r)
    check_11_http_node(all_nodes, r)
    check_12_space_id(data, all_nodes, r)
    check_13_sql_variables(all_nodes, r)
    check_13b_rownum_trap(all_nodes, edges, r)
    check_13c_db_field_mapping(all_nodes, r)
    check_14b_edge_format(data, all_nodes, r)
    check_15_external_data_title(all_nodes, r)
    check_16_intent_node(all_nodes, r)
    check_17_selector_ports(all_nodes, edges, r)
    check_18_error_branch(all_nodes, edges, r)
    check_19_set_variable(nodes, r)  # set_variable 需从容器内部找
    check_20_kb_query_param(all_nodes, r)
    check_21_kb_write(all_nodes, r)
    check_22_loop_schema(nodes, r)

    return r


def main():
    if len(sys.argv) < 2:
        print("用法: python coze_workflow_validator.py <workflow.json>")
        print()
        print("本脚本自动检查 Coze 工作流 JSON 的结构性问题，")
        print("覆盖 Phase 3.5 中 17+ 项可自动化的自检规则。")
        sys.exit(1)

    filepath = sys.argv[1]
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = validate_workflow(data)
    print(result.summary())
    sys.exit(1 if result.has_failures else 0)


if __name__ == "__main__":
    main()
