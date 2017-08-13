#!/usr/bin/make


install:
	rsync -aiHX tree/ debian/tmp
