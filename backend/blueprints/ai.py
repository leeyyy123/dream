"""
AI相关API接口
提供关键词提取、梦境分析、AI对话等功能
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.status import Status
from sql.database import get_db
from services.AIService import get_ai_service
from sql.AIChatSql import SaveAIChatHistory, GetAIChatHistory, DeleteAIChatHistory

# 创建蓝图
ai_bp = Blueprint('ai', __name__, url_prefix='/AI')


@ai_bp.before_request
def handle_options():
    """处理跨域预检请求"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight'})
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@ai_bp.route('/ExtractKeywords', methods=['POST', 'OPTIONS'])
@jwt_required()
def extract_keywords():
    """
    从梦境描述中提取关键词
    请求体: { "content": "梦境内容" }
    """
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify(Status.ParamsError.ToResponse("缺少梦境内容"))

        dream_content = data['content'].strip()
        if not dream_content:
            return jsonify(Status.ParamsError.ToResponse("梦境内容不能为空"))

        # 调用AI服务提取关键词
        ai_service = get_ai_service()
        result = ai_service.extract_keywords(dream_content)

        if result['success']:
            response = Status.OK.ToResponse("关键词提取成功")
            response['Data'] = result['data']
            return jsonify(response)
        else:
            return jsonify({
                'Code': 500,
                'Msg': result.get('error', '关键词提取失败')
            })

    except Exception as e:
        print(f"关键词提取异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))


@ai_bp.route('/AnalyzeDream', methods=['POST', 'OPTIONS'])
@jwt_required()
def analyze_dream():
    """
    分析梦境内容
    请求体: { "content": "梦境内容", "context": "额外上下文（可选）" }
    """
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify(Status.ParamsError.ToResponse("缺少梦境内容"))

        dream_content = data['content'].strip()
        if not dream_content:
            return jsonify(Status.ParamsError.ToResponse("梦境内容不能为空"))

        context = data.get('context', '')

        # 调用AI服务分析梦境
        ai_service = get_ai_service()
        analysis = ai_service.analyze_dream(dream_content, context)

        response = Status.OK.ToResponse("梦境分析成功")
        response['Data'] = {
            'analysis': analysis
        }
        return jsonify(response)

    except Exception as e:
        print(f"梦境分析异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))


@ai_bp.route('/Chat', methods=['POST', 'OPTIONS'])
@jwt_required()
def chat():
    """
    AI梦境对话
    请求体: {
        "question": "用户问题",
        "dreamContext": "梦境内容/分析报告",
        "chatHistory": [{"role": "user/assistant", "content": "..."}] (可选)
    }
    """
    try:
        print("[AI聊天] 收到请求")

        data = request.get_json()
        if not data:
            print("[AI聊天] 错误: 缺少请求数据")
            return jsonify(Status.ParamsError.ToResponse("缺少请求数据"))

        question = data.get('question', '').strip()
        dream_context = data.get('dreamContext', '').strip()
        chat_history = data.get('chatHistory', [])

        print(f"[AI聊天] 问题长度: {len(question)}, 上下文长度: {len(dream_context)}")

        if not question:
            print("[AI聊天] 错误: 问题为空")
            return jsonify(Status.ParamsError.ToResponse("问题不能为空"))

        if not dream_context:
            print("[AI聊天] 错误: 缺少梦境上下文")
            return jsonify(Status.ParamsError.ToResponse("缺少梦境上下文"))

        # 调用AI服务进行对话
        print("[AI聊天] 正在调用AI服务...")
        ai_service = get_ai_service()
        reply = ai_service.chat_about_dream(question, dream_context, chat_history)

        print(f"[AI聊天] AI回复成功，回复长度: {len(reply)}")

        response = Status.OK.ToResponse("对话成功")
        response['Data'] = {
            'reply': reply
        }
        return jsonify(response)

    except ValueError as e:
        # API Key未配置
        print(f"[AI聊天] 配置错误: {str(e)}")
        return jsonify({
            'Code': 500,
            'Msg': f"AI服务配置错误: {str(e)}"
        })
    except Exception as e:
        import traceback
        print(f"[AI聊天] 异常: {str(e)}")
        print(f"[AI聊天] 异常追踪:\n{traceback.format_exc()}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))


@ai_bp.route('/GenerateSummary', methods=['POST', 'OPTIONS'])
@jwt_required()
def generate_summary():
    """
    生成多梦总结分析
    请求体: {
        "dreams": [
            {"title": "", "content": "", "date": ""},
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        if not data or 'dreams' not in data:
            return jsonify(Status.ParamsError.ToResponse("缺少梦境数据"))

        dreams = data['dreams']
        if not isinstance(dreams, list) or len(dreams) == 0:
            return jsonify(Status.ParamsError.ToResponse("梦境数据格式错误"))

        # 调用AI服务生成总结
        ai_service = get_ai_service()
        summary = ai_service.generate_dream_summary(dreams)

        response = Status.OK.ToResponse("总结生成成功")
        response['Data'] = {
            'summary': summary
        }
        return jsonify(response)

    except Exception as e:
        print(f"生成总结异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))


@ai_bp.route('/GetEmotionSuggestions', methods=['POST', 'OPTIONS'])
@jwt_required()
def get_emotion_suggestions():
    """
    根据情绪获取建议
    请求体: { "emotions": ["快乐", "焦虑", ...] }
    """
    try:
        data = request.get_json()
        if not data or 'emotions' not in data:
            return jsonify(Status.ParamsError.ToResponse("缺少情绪数据"))

        emotions = data['emotions']
        if not isinstance(emotions, list) or len(emotions) == 0:
            return jsonify(Status.ParamsError.ToResponse("情绪数据格式错误"))

        # 调用AI服务获取建议
        ai_service = get_ai_service()
        suggestions = ai_service.get_emotion_suggestions(emotions)

        response = Status.OK.ToResponse("获取建议成功")
        response['Data'] = {
            'suggestions': suggestions
        }
        return jsonify(response)

    except Exception as e:
        print(f"获取建议异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))


@ai_bp.route('/AnalyzeDreamWithKeywords', methods=['POST', 'OPTIONS'])
@jwt_required()
def analyze_dream_with_keywords():
    """
    分析梦境并提取关键词（组合接口）
    请求体: { "content": "梦境内容", "context": "额外上下文（可选）" }
    """
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify(Status.ParamsError.ToResponse("缺少梦境内容"))

        dream_content = data['content'].strip()
        if not dream_content:
            return jsonify(Status.ParamsError.ToResponse("梦境内容不能为空"))

        context = data.get('context', '')

        # 调用AI服务
        ai_service = get_ai_service()

        # 提取关键词
        keywords_result = ai_service.extract_keywords(dream_content)

        # 分析梦境
        analysis = ai_service.analyze_dream(dream_content, context)

        response = Status.OK.ToResponse("分析成功")
        response['Data'] = {
            'keywords': keywords_result.get('data', {}) if keywords_result['success'] else {},
            'analysis': analysis
        }
        return jsonify(response)

    except Exception as e:
        print(f"梦境分析异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))


@ai_bp.route('/GetChatHistory', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_chat_history():
    """
    获取AI对话历史
    参数: sourceType (dream/analysis), sourceId (梦境ID或分析ID)
    """
    try:
        source_type = request.args.get('sourceType', 'dream')
        source_id = request.args.get('sourceId')

        if not source_id:
            return jsonify(Status.ParamsError.ToResponse("缺少sourceId参数"))

        try:
            source_id = int(source_id)
        except ValueError:
            return jsonify(Status.ParamsError.ToResponse("sourceId必须是整数"))

        connection = get_db()
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 获取当前用户ID
        current_email = get_jwt_identity()
        with connection.cursor() as cursor:
            cursor.execute("SELECT UserID FROM Users WHERE Email = %s", (current_email,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify(Status.UserUnexist.ToResponse())
            user_id = user_result['UserID']

        # 获取对话历史
        chat_history, status = GetAIChatHistory(connection, user_id, source_type, source_id)

        if status == Status.OK:
            response = Status.OK.ToResponse("获取对话历史成功")
            response['Data'] = chat_history
            return jsonify(response)
        elif status == Status.ResultEmpty:
            # 没有历史记录，返回空
            response = Status.OK.ToResponse("暂无对话历史")
            response['Data'] = {
                'Messages': []
            }
            return jsonify(response)
        else:
            return jsonify(status.ToResponse())

    except Exception as e:
        import traceback
        print(f"获取对话历史异常: {str(e)}")
        print(f"异常追踪:\n{traceback.format_exc()}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))


@ai_bp.route('/SaveChatHistory', methods=['POST', 'OPTIONS'])
@jwt_required()
def save_chat_history():
    """
    保存AI对话历史
    请求体: {
        "sourceType": "dream" 或 "analysis",
        "sourceId": 梦境ID或分析ID,
        "messages": [{"role": "user/assistant", "content": "..."}]
    }
    """
    try:
        print("[AI保存] 收到请求")

        data = request.get_json()
        if not data:
            return jsonify(Status.ParamsError.ToResponse("缺少请求数据"))

        source_type = data.get('sourceType', 'dream')
        source_id = data.get('sourceId')
        messages = data.get('messages', [])

        if source_id is None:
            return jsonify(Status.ParamsError.ToResponse("缺少sourceId"))

        if not isinstance(messages, list):
            return jsonify(Status.ParamsError.ToResponse("messages必须是数组"))

        print(f"[AI保存] 来源类型: {source_type}, 来源ID: {source_id}, 消息数: {len(messages)}")

        connection = get_db()
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 获取当前用户ID
        current_email = get_jwt_identity()
        with connection.cursor() as cursor:
            cursor.execute("SELECT UserID FROM Users WHERE Email = %s", (current_email,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify(Status.UserUnexist.ToResponse())
            user_id = user_result['UserID']

        # 保存对话历史
        status = SaveAIChatHistory(connection, user_id, source_type, source_id, messages)

        if status == Status.OK:
            print(f"[AI保存] 保存成功")
            response = Status.OK.ToResponse("保存对话历史成功")
            return jsonify(response)
        else:
            return jsonify(status.ToResponse())

    except Exception as e:
        import traceback
        print(f"保存对话历史异常: {str(e)}")
        print(f"异常追踪:\n{traceback.format_exc()}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))


@ai_bp.route('/DeleteChatHistory', methods=['POST', 'OPTIONS'])
@jwt_required()
def delete_chat_history():
    """
    删除AI对话历史
    请求体: {
        "sourceType": "dream" 或 "analysis",
        "sourceId": 梦境ID或分析ID
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(Status.ParamsError.ToResponse("缺少请求数据"))

        source_type = data.get('sourceType', 'dream')
        source_id = data.get('sourceId')

        if source_id is None:
            return jsonify(Status.ParamsError.ToResponse("缺少sourceId"))

        connection = get_db()
        if isinstance(connection, Status):
            return jsonify(connection.ToResponse())

        # 获取当前用户ID
        current_email = get_jwt_identity()
        with connection.cursor() as cursor:
            cursor.execute("SELECT UserID FROM Users WHERE Email = %s", (current_email,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify(Status.UserUnexist.ToResponse())
            user_id = user_result['UserID']

        # 删除对话历史
        status = DeleteAIChatHistory(connection, user_id, source_type, source_id)

        if status == Status.OK:
            response = Status.OK.ToResponse("删除对话历史成功")
            return jsonify(response)
        else:
            return jsonify(status.ToResponse())

    except Exception as e:
        print(f"删除对话历史异常: {str(e)}")
        return jsonify(Status.ErrorRequest.ToResponse(str(e)))
