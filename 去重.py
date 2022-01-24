# -*- coding: utf-8 -*-
import pandas as pd

info = pd.read_csv("2017_all.csv")
info = info.drop_duplicates("id",inplace=False)
info.to_csv("2017_all_new.csv")

