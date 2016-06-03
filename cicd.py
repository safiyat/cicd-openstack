import sys
import json
import time
sys.path.insert(0, 'utils.zip')
from utils import get_parser
import keystoneutils
import novautils

from vm_info import get_vm_list

p = get_parser()
args = p.parse_args()
session = keystoneutils.get_session(args)

# Collect detailed information about all the VMs in SDCloud
nc = novautils.get_client(session)
get_vm_list(nc=nc)
