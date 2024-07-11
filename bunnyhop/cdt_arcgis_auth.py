"""
    A set of functionality to manage credentials to publish to CDT's ArcGIS Online instance.
    In short, ArcGIS has two methods - the first is a token that lasts up to a year, but
    needs to be manually rotated. The second is OAuth2 credentials that last up to two weeks,
    but can be rotated programatically (I think we should be able to do this with arcpy).

    So, this file includes functionality that, given a starting set of credentials, begins
    managing 2-week OAuth2 credentials so that they can be automatically rotated.

    IMPORTANT: This will need to persist credentials to disk - we need to do a few things
    to minimize security implications of this:
        1. It wouldn't hurt to do some kind of 2-way encryption on the stored data. Even if
        the encryption key is hardcoded here, it means that the value on disk can't be used
        as-is, which is good.
        2. The user profile, or at least the storage folder,
        that this runs under should be encrypted by Windows to ensure
        that no other account on the device can read its data
        3. Ideally there is also full-disk encryption, but with item 2, that's less critical.
        We still need item 2 even if we do full-disk encryption because the threat model is
        if someone else gets credentials for *another* account that can access the machine
        this runs on, we don't want them to be able to read the publishing key and then
        use it. If the user profile is separately encrypted, it won't be possible for
        them to retrieve the value from another account.

    Alternatively, it seems like we might want to use the Windows Credential Manager (accessible
    via the keyring package)

    This all starts with an initialization value. So even if the user account this runs under
    is lost for some reason, we can set it up again with a new initialization credential (that
    immediately gets rotated by the application).

    What we also need to do is set up the rest of this codebase to rotate the key automatically
    whenever it runs, and *if* we don't run the rest of the code more than every two weeks,
    we at least need to run this. My guess is this will looks something like a daily run:
        1. to rotate the key
        2. then to check if there is a data update and run the rest of the code

"""


from typing import Any


params:dict[str, Any] = {
    "access_token": "",
    "expires_in": 1800,
    "ssl": True,
    "username": "nick.santos_california"
}