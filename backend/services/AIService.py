"""
智谱AI服务模块
提供关键词提取、情绪分析、梦境分析等功能
"""

import json
import os
from typing import List, Dict, Optional
from zhipuai import ZhipuAI

# 从环境变量获取API Key
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY', '')

printdebug = True


class AIService:
    """智谱AI服务类"""

    def __init__(self, api_key: str = None):
        """初始化AI服务"""
        self.api_key = api_key or ZHIPU_API_KEY
        if not self.api_key:
            raise ValueError("智谱AI API Key未配置，请设置环境变量 ZHIPU_API_KEY")

        self.client = ZhipuAI(api_key=self.api_key)

        # 可用的情绪列表
        self.available_emotions = [
            "快乐", "焦虑", "恐惧", "愤怒", "悲伤",
            "惊讶", "平静", "兴奋", "困惑", "期待"
        ]

        # 可用的梦境类型
        self.available_dream_types = [
            "噩梦", "清醒梦", "预知梦", "重复梦", "飞行梦",
            "坠落梦", "追逐梦", "考试梦", "牙齿脱落", "赤身裸体",
            "迷路梦", "死亡梦", "超自然梦", "童年回忆", "日常生活"
        ]

    def _call_ai(self, messages: List[Dict], model: str = "glm-4-flash") -> str:
        """调用智谱AI接口"""
        try:
            if printdebug:
                print(f"[AI服务] 正在调用智谱AI，模型: {model}")
                print(f"[AI服务] API Key状态: {'已配置' if self.api_key else '未配置'}")
                print(f"[AI服务] 请求消息数量: {len(messages)}")

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            result = response.choices[0].message.content

            if printdebug:
                print(f"[AI服务] 调用成功，响应长度: {len(result)}")

            return result

        except Exception as e:
            import traceback
            error_detail = str(e)
            error_trace = traceback.format_exc()

            if printdebug:
                print(f"[AI服务] 调用失败:")
                print(f"  错误类型: {type(e).__name__}")
                print(f"  错误详情: {error_detail}")
                print(f"  错误追踪:\n{error_trace}")

            # 重新抛出包含详细信息的异常
            raise Exception(f"AI服务调用失败: {error_detail}")

    def extract_keywords(self, dream_content: str) -> Dict:
        """
        从梦境描述中提取关键词

        Args:
            dream_content: 梦境内容描述

        Returns:
            Dict: {
                "keywords": [
                    {"text": "关键词", "category": "分类", "weight": 权重}
                ],
                "emotions": ["情绪1", "情绪2"],
                "dream_types": ["类型1", "类型2"]
            }
        """
        system_prompt = """你是一个专业的梦境分析助手。请从用户的梦境描述中提取关键信息。

你需要：
1. 提取关键词（人物、地点、物品、事件、象征符号等）
2. 识别梦境中的情绪
3. 判断梦境类型

关键词分类：
- person: 人物（如：妈妈、朋友、陌生人、明星等）
- place: 地点（如：学校、家里、森林、海边等）
- object: 物品（如：手机、钱、钥匙等）
- event: 事件（如：考试、飞行、坠落、追逐等）
- symbol: 象征符号（如：月亮、水、火、蛇等）
- other: 其他

关键词权重：
- 1: 一般提及
- 2: 重要元素
- 3: 核心元素

可用情绪：快乐、焦虑、恐惧、愤怒、悲伤、惊讶、平静、兴奋、困惑、期待

可用梦境类型：噩梦、清醒梦、预知梦、重复梦、飞行梦、坠落梦、追逐梦、考试梦、牙齿脱落、赤身裸体、迷路梦、死亡梦、超自然梦、童年回忆、日常生活

请以JSON格式返回结果：
{
    "keywords": [
        {"text": "关键词", "category": "分类", "weight": 权重}
    ],
    "emotions": ["情绪1", "情绪2"],
    "dream_types": ["类型1", "类型2"]
}

只返回JSON，不要其他内容。"""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"梦境内容：\n{dream_content}"}
            ]

            response = self._call_ai(messages)

            # 尝试解析JSON响应
            try:
                # 清理可能的markdown标记
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()

                result = json.loads(response)

                # 过滤和验证数据
                if "keywords" in result:
                    result["keywords"] = [
                        kw for kw in result["keywords"]
                        if isinstance(kw, dict) and "text" in kw and "category" in kw
                    ][:20]  # 限制最多20个关键词

                if "emotions" in result:
                    result["emotions"] = [
                        e for e in result["emotions"]
                        if e in self.available_emotions
                    ][:5]  # 限制最多5个情绪

                if "dream_types" in result:
                    result["dream_types"] = [
                        t for t in result["dream_types"]
                        if t in self.available_dream_types
                    ][:3]  # 限制最多3个类型

                return {
                    "success": True,
                    "data": result
                }

            except json.JSONDecodeError as e:
                if printdebug:
                    print(f"JSON解析失败: {e}, 响应内容: {response}")
                return {
                    "success": False,
                    "error": "AI响应格式错误"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def analyze_dream(self, dream_content: str, context: str = "") -> str:
        """
        分析梦境内容

        Args:
            dream_content: 梦境内容
            context: 额外上下文（如用户最近的生活状态）

        Returns:
            str: 梦境分析报告
        """
        system_prompt = """你是一位专业的梦境分析师和心理咨询师。请为用户提供深入、温暖、有启发性的梦境分析。

分析时请包含：
1. 梦境象征解读：解释梦中主要元素的心理学含义
2. 情绪分析：分析梦境反映的潜意识情绪
3. 生活关联：联系现实生活，提供可能的解释
4. 积极启示：提供积极的建议和思考方向

请用温暖、专业、有同理心的语言进行分析。避免过于负面的解读，多从成长和自我认知的角度给予启发。

分析长度控制在500-800字。"""

        user_prompt = f"""梦境内容：
{dream_content}
"""

        if context:
            user_prompt += f"\n用户背景：\n{context}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return self._call_ai(messages)

    def chat_about_dream(self, question: str, dream_context: str, chat_history: List[Dict] = None) -> str:
        """
        关于梦境的对话

        Args:
            question: 用户问题
            dream_context: 梦境内容或分析报告
            chat_history: 对话历史

        Returns:
            str: AI回复
        """
        system_prompt = """你是一位温暖、专业的梦境分析师和心理咨询师。你擅长：

1. 倾听用户的问题和困惑
2. 从心理学角度解读梦境元素
3. 提供积极、有启发性的见解
4. 引导用户进行自我反思
5. 给出实用的建议

回复风格：
- 温暖、有同理心
- 专业但不生硬
- 积极正面
- 引导而非说教
- 简洁明了，避免过度解读

每次回复控制在100-300字。"""

        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]

        # 如果有对话历史，添加最近几轮（在system消息之后）
        if chat_history:
            recent_history = chat_history[-10:]  # 取最近10条消息
            for msg in reversed(recent_history):  # 倒序插入以保持正确顺序
                messages.insert(1, msg)

        # 添加当前问题和上下文
        context_msg = f"用户梦境/分析内容：\n{dream_context}\n\n用户问题：{question}"
        messages.append({"role": "user", "content": context_msg})

        return self._call_ai(messages)

    def generate_dream_summary(self, dreams: List[Dict]) -> str:
        """
        生成多梦总结分析

        Args:
            dreams: 梦境列表 [{"title": "", "content": "", "date": ""}, ...]

        Returns:
            str: 总结分析报告
        """
        # 构建梦境摘要
        dreams_summary = ""
        for i, dream in enumerate(dreams[:10], 1):  # 最多分析10个梦境
            dreams_summary += f"\n【梦境{i}】{dream.get('date', '')}\n"
            dreams_summary += f"标题：{dream.get('title', '无标题')}\n"
            dreams_summary += f"内容：{dream.get('content', '')[:200]}...\n"

        system_prompt = """你是一位专业的梦境分析师。请为用户的多梦记录进行总结分析。

分析要点：
1. 整体主题：这些梦境反映了什么主题或关注点
2. 情绪模式：情绪变化和趋势
3. 重复元素：反复出现的人物、场景、符号
4. 潜意识信息：可能反映的潜意识想法
5. 成长建议：基于分析给出的建议

报告格式：
- 清晰分段
- 每部分有小标题
- 总长度600-1000字
- 温暖、积极、有启发"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"我的梦境记录：{dreams_summary}\n\n请帮我分析总结。"}
        ]

        return self._call_ai(messages)

    def get_emotion_suggestions(self, emotions: List[str]) -> str:
        """
        根据情绪给出建议

        Args:
            emotions: 情绪列表

        Returns:
            str: 建议内容
        """
        emotion_str = "、".join(emotions)

        system_prompt = """你是一位温暖的心理咨询师。用户在梦境中体验了某些情绪，请给出理解和建议。

建议要点：
1. 情绪正常化：让用户理解这些情绪是正常的
2. 原因分析：可能的原因
3. 应对策略：实用的调节方法
4. 积极视角：从这些情绪中获得的成长

回复控制在200-400字，温暖、实用。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"我在梦中感受到{emotion_str}等情绪，请给我一些建议。"}
        ]

        return self._call_ai(messages)


# 创建全局AI服务实例
_ai_service = None


def get_ai_service() -> AIService:
    """获取AI服务实例（单例模式）"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
