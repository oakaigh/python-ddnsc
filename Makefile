PACKAGE_NAME=python-ddnsc
SYSTEMD_UNIT_NAME=ddnsc-daemon


install:
	sudo python3 -m pip install .
	sudo config/systemd_install.py --unit-name=$(SYSTEMD_UNIT_NAME)
	sudo systemctl daemon-reload

remove:
	sudo python3 -m pip uninstall $(PACKAGE_NAME)
	sudo config/systemd_install.py --remove --unit-name=$(SYSTEMD_UNIT_NAME)
	sudo systemctl daemon-reload

deploy:
	sudo systemctl disable --now $(SYSTEMD_UNIT_NAME) || true
	sudo make install && sudo systemctl enable --now $(SYSTEMD_UNIT_NAME)

.PHONY: install remove deploy
