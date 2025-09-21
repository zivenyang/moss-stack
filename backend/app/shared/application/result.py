from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, ConfigDict  # <-- 导入 ConfigDict

T = TypeVar("T")
# 我们将 E 的类型约束放宽一点，使其更通用
E = TypeVar("E")


class Result(BaseModel, Generic[T, E]):
    """
    A standardized result object for application layer services.
    It encapsulates either a successful value or an error.
    """

    is_success: bool
    value: Optional[T] = None
    error: Optional[E] = None

    # --- 关键修改 ---
    # 使用 model_config 字典来配置 Pydantic V2 的行为
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def success(cls, value: T) -> "Result[T, Any]":
        return cls(is_success=True, value=value)

    @classmethod
    def failure(cls, error: E) -> "Result[Any, E]":
        # 在失败时，确保 value 字段为 None
        return cls(is_success=False, value=None, error=error)

    def get_value(self) -> T:
        """Returns the value if the result is a success, otherwise raises the error."""
        if self.is_success and self.value is not None:
            return self.value

        # 抛出错误
        if self.error:
            # Pydantic V2 会将 error 视为一个普通属性，所以可以直接抛出
            if isinstance(self.error, Exception):
                raise self.error
            else:
                # 如果 error 不是一个 Exception 实例，则抛出一个通用异常
                raise Exception(f"Result failed with non-exception error: {self.error}")

        raise Exception("Unknown error in a failed Result without a specific error.")
