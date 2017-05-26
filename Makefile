test: build/venv
	@( . build/venv/bin/activate;  \
	    cd src && \
		nosetests --with-xunit --xunit-file=../build/nosetests.xml \
			--with-coverage --cover-package=cassandras3 --cover-xml --cover-xml-file=../build/coverage.xml \
			test \
	)

clean:
	rm -Rf build/

build/venv: build/venv/bin/activate

build/venv/bin/activate: requirements.txt
	@mkdir -p build
	@test -d build/venv || virtualenv --system-site-packages build/venv
	@( . build/venv/bin/activate;  \
		pip install -r requirements.txt; \
		pip install -r src/test/requirements.txt; \
	)

lint: build/venv
	@( . build/venv/bin/activate; \
		find src -not -path 'src/test*' -name '*.py' | xargs pylint --rcfile pylintrc \
	)

composetest:
	-docker-compose kill
	-docker-compose rm -f
	docker-compose build
	docker-compose run test

.PHONY: composetest test
