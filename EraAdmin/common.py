from EraAdmin.models import \
    SysDictionary as SysDictionaryModel, \
    SysDictionaryData as SysDictionaryDataModel


def sys_dict_data(code):
    ret = SysDictionaryModel.get_data(code)
    data = []
    for item in ret:
        item: SysDictionaryDataModel
        data.append(item.toDict())
    return data
def sys_config_data(code):
    return {}