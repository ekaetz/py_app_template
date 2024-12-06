class Utils(object):

    @staticmethod
    def merge_dict(base_dict: {}, update_dict: {}):
        for key, value, in update_dict.items():
            if isinstance(value, dict):
                if key in base_dict:
                    Utils.mergeDict(base_dict[key], value)
                else:
                    base_dict[key] = value
            else:
                base_dict[key] = value
        return base_dict