import pandas as pd
df=pd.read_csv('Data/image_data.csv')


def Name_from_id(id_input):
    id_column = list(df['Id'])
    names_list = list(df['Name'])
    ind = id_column.index(id_input)
    name = names_list(ind)
    return name

def PhoneNumber_from_id(id_input):
    id_column=list(df['Id'])
    phone_list=list(df['Phone_Number'])
    ind=id_column.index(id_input)
    phone=phone_list(ind)
    return phone

def General_Information_from_id(id_input):
    id_column=list(df['Id'])
    info_list=list(df['General_Information'])
    ind=id_column.index(id_input)
    info=info_list(ind)
    return info

def Relation(id_input):
    id_column=list(df['Id'])
    relation_list=list(df['Relation'])
    ind=id_column.index(id_input)
    relation=relation_list(ind)
    return relation