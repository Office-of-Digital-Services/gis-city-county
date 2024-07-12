"""
    After we run the joins, we'll want to compare the current version to the previous one and have some measure of how much has
    changed. If a *lot* has changed, I think we'll want to skip automatic publishing and instead notify maintainers
    to check the output and run the code again, forcing it to issue the update if it's reasonable. But many changes
    may instead be an issue running the code, since we don't expect very many cities/counties to change all at once.
"""