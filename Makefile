build: AutoScreenShot.py
	pyinstaller -F -w $^
clean:
	rm -rf build dist Screenshots *.spec
.PHONY: clean
