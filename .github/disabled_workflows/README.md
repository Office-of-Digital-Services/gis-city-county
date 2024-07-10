# Disabled GitHub Actions

I'd started writing up GitHub Actions to automatically run the code, but it looks like arcpy
still can't run from a VM that doesn't have ArcGIS Pro installed. We could do it with Azure
Pipelines if we built a custom runner that has ArcGIS Pro
though, which might be a nice option for testing changes to the script before updating a live service.

Disabling the action for now. We'll revisit this later.
