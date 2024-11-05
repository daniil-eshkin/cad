sample1:
	python3 main.py samples/1/conf.yml samples/1/model.json samples/1/input.json

sample2:
	python3 main.py samples/2/conf.yml samples/2/model.json samples/2/input.json

sample2_1:
	python3 main.py samples/2_1/conf.yml samples/2_1/model.json samples/2_1/input.json

sample3:
	python3 main.py samples/3/conf.yml samples/3/model.json samples/3/input.json

sample4:
	python3 main.py samples/4/conf.yml samples/4/model.json samples/4/input.json

sample5:
	python3 main.py samples/5/conf.yml samples/5/model.json samples/5/input.json

sample6:
	python3 main.py samples/6/conf.yml samples/6/model.json samples/6/input.json

sample7:
	python3 main.py samples/7/conf.yml samples/7/model.json samples/7/input.json

test:
	python3 -m unittest discover cad/tests -p '*_test.py'
