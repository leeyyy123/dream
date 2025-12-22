from enum import Enum

printdebug = True  # 全局调试开关

class Status(Enum):
    # Success
    OK = 200
    ResultEmpty = 201
    SuperLogin = 202

    # Normal Errors
    AuthFailed = 500
    LoginFailed = 501
    ErrorPassword = 504
    UserExist = 502
    UserUnexist = 503

    # Parameter Error
    ParamsError = 540
    ErrorRequest = 530

    # Database Errors
    DatabaseConnectionError = 510
    DatabaseOperationError = 511
    RedisConnectionError = 512
    RedisOperationError = 513
    DatabaseInsertError = 514
    DatabaseUpdateError = 515
    DatabaseDeleteError = 516
    DatabaseSelectError = 517
    EmailSendFailed = 518

    # Login Error
    SigninVerifyCodeError = 520
    SigninVerifyCodeExpired = 521

    def ToResponse(self, Msg=None):
        """生成包含Code和Msg的JSON格式响应字典"""
        return {
            "Code": self.value,
            "Msg": Msg if Msg is not None else self.name
        }