"""
Error handling and monitoring utilities
"""
import time
import traceback
from typing import Any, Callable, Dict, List, Optional, Type, Union
from functools import wraps
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger
import json

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories"""
    NETWORK = "network"
    BROWSER = "browser"
    PARSING = "parsing"
    VALIDATION = "validation"
    API = "api"
    SYSTEM = "system"
    UNKNOWN = "unknown"

@dataclass
class ErrorInfo:
    """Error information container"""
    timestamp: datetime = field(default_factory=datetime.now)
    error_type: str = ""
    error_message: str = ""
    category: ErrorCategory = ErrorCategory.UNKNOWN
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""
    retry_count: int = 0
    resolved: bool = False

class ErrorTracker:
    """Track and analyze errors"""
    
    def __init__(self, max_errors: int = 1000):
        """Initialize error tracker"""
        self.max_errors = max_errors
        self.errors: List[ErrorInfo] = []
        self.error_counts: Dict[str, int] = {}
        self.last_cleanup = datetime.now()
    
    def record_error(self, error: Exception, category: ErrorCategory = ErrorCategory.UNKNOWN,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM, context: Dict[str, Any] = None):
        """Record an error"""
        error_info = ErrorInfo(
            error_type=type(error).__name__,
            error_message=str(error),
            category=category,
            severity=severity,
            context=context or {},
            stack_trace=traceback.format_exc()
        )
        
        self.errors.append(error_info)
        
        # Update error counts
        error_key = f"{error_info.error_type}:{error_info.category.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Cleanup old errors if needed
        self._cleanup_old_errors()
        
        # Log error
        log_level = self._get_log_level(severity)
        logger.log(log_level, f"Error recorded: {error_info.error_message}")
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [e for e in self.errors if e.timestamp >= cutoff_time]
        
        # Count by category
        category_counts = {}
        severity_counts = {}
        
        for error in recent_errors:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        return {
            "total_errors": len(recent_errors),
            "by_category": category_counts,
            "by_severity": severity_counts,
            "most_common": self._get_most_common_errors(recent_errors),
            "time_period_hours": hours
        }
    
    def _cleanup_old_errors(self):
        """Remove old errors to prevent memory issues"""
        if len(self.errors) > self.max_errors:
            # Keep only the most recent errors
            self.errors = self.errors[-self.max_errors:]
        
        # Cleanup every hour
        if datetime.now() - self.last_cleanup > timedelta(hours=1):
            # Remove errors older than 7 days
            cutoff_time = datetime.now() - timedelta(days=7)
            self.errors = [e for e in self.errors if e.timestamp >= cutoff_time]
            self.last_cleanup = datetime.now()
    
    def _get_log_level(self, severity: ErrorSeverity) -> str:
        """Get log level based on severity"""
        mapping = {
            ErrorSeverity.LOW: "DEBUG",
            ErrorSeverity.MEDIUM: "WARNING",
            ErrorSeverity.HIGH: "ERROR",
            ErrorSeverity.CRITICAL: "CRITICAL"
        }
        return mapping.get(severity, "WARNING")
    
    def _get_most_common_errors(self, errors: List[ErrorInfo], limit: int = 5) -> List[Dict[str, Any]]:
        """Get most common errors"""
        error_counts = {}
        
        for error in errors:
            key = f"{error.error_type}: {error.error_message[:50]}"
            error_counts[key] = error_counts.get(key, 0) + 1
        
        # Sort by count and return top N
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [{"error": error, "count": count} for error, count in sorted_errors[:limit]]

# Global error tracker instance
error_tracker = ErrorTracker()

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, 
                      backoff_factor: float = 2.0, max_delay: float = 60.0,
                      exceptions: tuple = (Exception,)):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    # Record error
                    category = _categorize_error(e)
                    severity = ErrorSeverity.MEDIUM if attempt < max_retries else ErrorSeverity.HIGH
                    
                    error_tracker.record_error(
                        e, category, severity, 
                        {"function": func.__name__, "attempt": attempt + 1, "max_retries": max_retries}
                    )
                    
                    if attempt < max_retries:
                        # Calculate delay with exponential backoff
                        delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            # Re-raise the last exception if all retries failed
            raise last_exception
        
        return wrapper
    return decorator

def handle_errors(category: ErrorCategory = ErrorCategory.UNKNOWN, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 reraise: bool = True, default_return: Any = None):
    """
    Decorator for handling and logging errors
    
    Args:
        category: Error category
        severity: Error severity
        reraise: Whether to re-raise the exception
        default_return: Default value to return if error occurs and reraise=False
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            
            except Exception as e:
                # Record error
                error_tracker.record_error(
                    e, category, severity,
                    {"function": func.__name__, "args": str(args)[:100], "kwargs": str(kwargs)[:100]}
                )
                
                if reraise:
                    raise
                else:
                    logger.warning(f"Error in {func.__name__} handled, returning default: {str(e)}")
                    return default_return
        
        return wrapper
    return decorator

def _categorize_error(error: Exception) -> ErrorCategory:
    """Categorize error based on type and message"""
    error_type = type(error).__name__
    error_message = str(error).lower()
    
    # Network-related errors
    if any(keyword in error_message for keyword in ['connection', 'timeout', 'network', 'dns', 'socket']):
        return ErrorCategory.NETWORK
    
    # Browser-related errors
    if any(keyword in error_message for keyword in ['webdriver', 'selenium', 'chrome', 'browser']):
        return ErrorCategory.BROWSER
    
    # Parsing-related errors
    if any(keyword in error_message for keyword in ['parse', 'json', 'xml', 'html', 'beautifulsoup']):
        return ErrorCategory.PARSING
    
    # Validation errors
    if any(keyword in error_message for keyword in ['validation', 'invalid', 'missing', 'required']):
        return ErrorCategory.VALIDATION
    
    # API errors
    if any(keyword in error_message for keyword in ['api', 'key', 'quota', 'rate limit', 'unauthorized']):
        return ErrorCategory.API
    
    # System errors
    if any(keyword in error_message for keyword in ['memory', 'disk', 'permission', 'file', 'directory']):
        return ErrorCategory.SYSTEM
    
    return ErrorCategory.UNKNOWN

class HealthMonitor:
    """Monitor system health and performance"""
    
    def __init__(self):
        """Initialize health monitor"""
        self.start_time = datetime.now()
        self.metrics = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "average_response_time": 0.0,
            "last_success": None,
            "last_failure": None
        }
        self.response_times = []
        self.max_response_times = 100  # Keep last 100 response times
    
    def record_request(self, success: bool, response_time: float):
        """Record a request and its outcome"""
        self.metrics["requests_total"] += 1
        
        if success:
            self.metrics["requests_successful"] += 1
            self.metrics["last_success"] = datetime.now()
        else:
            self.metrics["requests_failed"] += 1
            self.metrics["last_failure"] = datetime.now()
        
        # Track response times
        self.response_times.append(response_time)
        if len(self.response_times) > self.max_response_times:
            self.response_times = self.response_times[-self.max_response_times:]
        
        # Update average response time
        self.metrics["average_response_time"] = sum(self.response_times) / len(self.response_times)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        uptime = datetime.now() - self.start_time
        success_rate = (
            self.metrics["requests_successful"] / self.metrics["requests_total"]
            if self.metrics["requests_total"] > 0 else 0
        )
        
        # Determine health status
        if success_rate >= 0.95:
            status = "healthy"
        elif success_rate >= 0.8:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "uptime_seconds": uptime.total_seconds(),
            "success_rate": success_rate,
            "metrics": self.metrics.copy(),
            "error_summary": error_tracker.get_error_summary(hours=1)
        }
    
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        status = self.get_health_status()
        return status["status"] == "healthy"

# Global health monitor instance
health_monitor = HealthMonitor()

def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = False
        
        try:
            result = func(*args, **kwargs)
            success = True
            return result
        
        except Exception as e:
            success = False
            raise
        
        finally:
            response_time = time.time() - start_time
            health_monitor.record_request(success, response_time)
    
    return wrapper

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func: Callable, *args, **kwargs):
        """Call function through circuit breaker"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self.last_failure_time is None:
            return True
        
        return (datetime.now() - self.last_failure_time).total_seconds() >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "closed"
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
