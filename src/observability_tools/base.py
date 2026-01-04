from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime, UTC
import time
from src.utils.logger import get_logger


logger = get_logger(__name__)

class BaseTool(ABC):

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        pass

    async def run(self, **kwargs) -> Dict[str, Any]:
        """
        Run the tool with timing and logging

        - estimate execution time
        - logging
        - error handling
        """

        start_time = time.time()
        logger.info(f"Tool '{self.name}' started", extra={"params": kwargs})

        try:
            result = await self.execute(**kwargs)
            execution_time = int((time.time() - start_time) * 1000)
            logger.info(
                f"Tool '{self.name}' completed",
                extra={"execution_time_ms": execution_time}
            )

            return {
                "success": True,
                "data" : result, 
                "execution_time_ms": execution_time,
                "timestamp": datetime.now(UTC).isoformat()
            }

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(
                f"Tool '{self.name}' failed: {str(e)}"
            )
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": execution_time,
                "timestamp": datetime.now(UTC).isoformat()
            }