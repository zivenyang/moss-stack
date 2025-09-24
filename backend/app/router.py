import importlib
import pkgutil
from typing import List
from fastapi import FastAPI, APIRouter

def autodiscover_and_include_routers(app: FastAPI, package_path: str) -> List:
    """
    Discovers, includes routers from a package, and returns the list of discovered
    modules for dependency injection wiring.

    Convention: Any module within the `package_path` that ends with `_router.py`
    and contains a variable named `router` of type `APIRouter` will be included.
    """
    discovered_modules = []
    package = importlib.import_module(package_path)
    
    # We create a main API router to apply the global /api/v1 prefix
    main_api_router = APIRouter()
    
    print(f"--- Starting router auto-discovery in '{package_path}' ---")
    
    # Use walk_packages to recursively find all modules
    for module_info in pkgutil.walk_packages(package.__path__, prefix=f"{package.__name__}."):
        
        # --- [核心修改] ---
        # 1. 建立一个简单而明确的约定：路由模块必须以 `_router.py` 结尾
        if not module_info.name.endswith('_router'):
            continue

        try:
            # 2. 动态导入这个符合约定的模块
            module = importlib.import_module(module_info.name)
            print(f"  🔍 Checking module: {module_info.name}")
            
            # 3. 检查模块中是否存在一个名为 'router' 的 APIRouter 实例
            if hasattr(module, "router"):
                router_obj = getattr(module, "router")
                if isinstance(router_obj, APIRouter):
                    # Router self-defines its prefix and tags
                    main_api_router.include_router(router_obj)
                    discovered_modules.append(module)
                    print(f"  ✅ SUCCESS: Auto-discovered and included router from: {module_info.name}")
                else:
                    print(f"  ⚠️ WARNING: Found 'router' in {module_info.name}, but it is not an APIRouter instance.")
            else:
                 print(f"  ℹ️ INFO: Module {module_info.name} matches pattern but has no 'router' attribute.")

        except ImportError as e:
            print(f"  ❌ ERROR: Could not import module {module_info.name}: {e}")
            
    app.include_router(main_api_router, prefix="/api/v1") # Apply the global prefix
    print("--- Router auto-discovery finished ---")
    return discovered_modules