import win32pdh

query = win32pdh.OpenQuery(None,0)
win32pdh.AddCounter(query.'Process ID',0)
win32pdh.CollectQueryData(query)
win32pdh.CloseQuery(query)

list = win32pdh.EnumObjects(None, None, 0, 1)
print list

items, names = win32pdh.EnumObjectItems(None, None, 'Process', -1)

print items
print names 
