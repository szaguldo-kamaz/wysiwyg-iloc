# WYSIWYG Indoor Localization

import sys
import pysurvive

ctx = pysurvive.init(sys.argv)

if ctx is None: # implies -help or similiar
    exit(-1)

def button_func(obj, eventtype, buttonid, axisids, axisvals):
    if eventtype == pysurvive.SURVIVE_INPUT_EVENT_BUTTON_UP:
        print("Button %d on %s/%s"%(buttonid, obj.contents.codename.decode('utf8'), obj.contents.serial_number.decode('utf8')))


keepRunning = True

pysurvive.install_button_fn(ctx, button_func)

print("Press the button on a tracker!")

while keepRunning and pysurvive.poll(ctx) == 0:
    pass

pysurvive.close(ctx)
