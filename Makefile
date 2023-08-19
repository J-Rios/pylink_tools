
install:
	sudo cp -a ../pylink_tools /opt
	sudo ln -s /opt/pylink_tools/src/jlink_dump.py /usr/local/bin/jlink_dump
	sudo ln -s /opt/pylink_tools/src/jlink_flash.py /usr/local/bin/jlink_flash
	sudo ln -s /opt/pylink_tools/src/jlink_info.py /usr/local/bin/jlink_info
	sudo ln -s /opt/pylink_tools/src/jlink_list.py /usr/local/bin/jlink_list
	sudo ln -s /opt/pylink_tools/src/jlink_mcu_info.py /usr/local/bin/jlink_mcu_info
	sudo ln -s /opt/pylink_tools/src/jlink_rtt.py /usr/local/bin/jlink_rtt

uninstall:
	sudo rm -f /usr/local/bin/jlink_*
	sudo rm -rf /opt/pylink_tools

reinstall: uninstall install
