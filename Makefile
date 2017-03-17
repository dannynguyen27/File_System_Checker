default:
	@echo This is a python script. Use make run to execute.
run:
	python lab3b.py

dist: README Makefile lab3b.py

	@if [ -a lab3b-004628653 ] ; \
	then \
		rm -r lab3b-004628653 ; \
	fi;

	@mkdir lab3b-004628653
	@cp {Makefile,README,lab3b.py} lab3b-004628653 
	@tar -czvf lab3b-004628653.tar.gz lab3b-004628653
	@rm -r lab3b-004628653

clean:
	-rm lab3b-004628653.tar.gz
	-rm lab3b_check.txt