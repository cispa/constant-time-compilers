all: prepare template

template: template.c
	gcc -Os template.c -o template -lm

prepare:
	rm -rf data
	mkdir data

clean:
	rm template 