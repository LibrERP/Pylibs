#!/usr/bin/env python
# coding: utf-8

# # References
# 
# - **ASCII Character Set (and CTRL-? escape sequences):** https://docstore.mik.ua/orelly/unix3/unixnut/appa_01.htm
# - **ASCII Escape Sequences (F-XX keys), ecc.:** https://en.wikipedia.org/wiki/ANSI_escape_code
# - **ASCII Escape Sequences (curson position, colors, ecc.):** http://ascii-table.com/ansi-escape-sequences.php
# 
# **NB:** Cursor position is controlled by CSI sequences (part os ASCII Escape Sequences)

# In[1]:


from copy import deepcopy
import datetime
from collections import defaultdict

import sys
sys.path = (['../../'] + sys.path)


from av2000_terminator import ConnectionParams, Tasker
from av2000_terminator.misc.exceptions import LoadingTimeout


avt = Tasker(
    ConnectionParams('10.1.1.1', 222, 'dido', 'dido', 99, 0.1)
)


suppliers_brief_list = list()

try:
    report_step = 150
    report_next = report_step
    
    t_now = datetime.datetime.now()
    print(f'[{t_now:%H:%M:%S.%f}] Download begin')
    
    for res in avt.suppliers_list():
        suppliers_brief_list = suppliers_brief_list + res
        if len(suppliers_brief_list) > report_next:
            report_next = report_next + report_step
            t_now = datetime.datetime.now()
            print(f'[{t_now:%H:%M:%S.%f}] Downloaded {len(suppliers_brief_list)} elements')
    # end for
    
    t_now = datetime.datetime.now()
    print(f'[{t_now:%H:%M:%S.%f}] Downloaded {len(suppliers_brief_list)} elements')
    print(f'[{t_now:%H:%M:%S.%f}] Downloaded end')
    
except LoadingTimeout as lte:
    raised_excp = lte
    
    print()
    print()
    print()
    print('    ERRORE    ' * 4)
    print()
    print()
    print()
# end try / except


# Check uniqueness of suppliers
s_counters = defaultdict(lambda: 0)

for x in suppliers_brief_list:
    s_id = x['codice']
    s_counters[s_id] = s_counters[s_id] + 1
# end for

s_non_unique = [x for x in s_counters.items() if x[1] != 1]
s_unique = [x for x in s_counters.items() if x[1] == 1]

print(f'Items in "s_counters": {len(s_counters)}')
print(f'Items in "s_non_unique": {len(s_non_unique)}')
print(f'Items in "s_unique": {len(s_unique)}')


suppliers_details_dict = dict()

s_ids = [x['codice'] for x in suppliers_brief_list]

t_start = datetime.datetime.now()
for s_d in avt.suppliers_batch_get(s_ids, procs_num=4):
    suppliers_details_dict[s_d['codice']] = s_d
# end for
t_end = datetime.datetime.now()

t_secs = round((t_end - t_start).total_seconds(), 2)

print()
print()
print()
print()
print(f'Downloaded {len(suppliers_details_dict)} items in {t_secs} secs')
