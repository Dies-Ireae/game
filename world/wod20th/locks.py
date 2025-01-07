"""
Custom lock functions for World of Darkness
"""

def has_splat(accessing_obj, accessed_obj, *args, **kwargs):
    """Check if character is of a specific splat"""
    if not args:
        return False
    if not hasattr(accessing_obj, 'db'):
        return False
    
    # Get the splat directly from the stats structure
    stats = accessing_obj.db.stats or {}
    splat = stats.get('other', {}).get('splat', {}).get('Splat', {}).get('perm', '')
    
    # Debug output
    print(f"Checking splat for {accessing_obj}: got '{splat}', comparing to '{args[0]}'")
    
    return splat.lower() == args[0].lower()

def has_type(accessing_obj, accessed_obj, *args, **kwargs):
    """Check if character is of a specific type"""
    if not args:
        return False
    if not hasattr(accessing_obj, 'db'):
        return False
    
    # Get the type directly from the stats structure
    stats = accessing_obj.db.stats or {}
    char_type = stats.get('identity', {}).get('lineage', {}).get('Type', {}).get('perm', '')
    
    # Debug output
    print(f"Checking type for {accessing_obj}: got '{char_type}', comparing to '{args[0]}'")
    
    return char_type.lower() == args[0].lower()

# Export the functions for use elsewhere
LOCK_FUNCS = {
    "has_splat": has_splat,
    "has_type": has_type
}
