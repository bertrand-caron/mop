EXECUTABLE = ../build/fragments

profile: gmon.out
	gprof $(EXECUTABLE) $<
.PHONY: profile

gmon.out:
	-$(../build/fragments)
