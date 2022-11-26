init:
	wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tgz
	tar -xf Python-3.8.10.tgz
	-(cd Python-3.8.10 && ./configure --enable-optimizations && make -k altinstall)
	./Python-3.8.10/python -m venv venv
	. venv/bin/activate && ./Python-3.8.10/python -m ensurepip --upgrade && pip install -r ./requirements.txt

clean:
	rm -rf venv Python-3.8.10*