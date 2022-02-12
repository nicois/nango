import asgiref

from . import monkey_patches

### Monkey Patches
asgiref.sync.sync_to_async = monkey_patches.patch_sync_to_async
