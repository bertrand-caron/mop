EXECUTABLE = ../build/fragments

profile: gmon.out
	echo 'WARNING: Compile "fragments" with profiling enabled by running "cmake .. -DCMAKE_BUILD_TYPE=Profile" in your "build" directory.'
	gprof $(EXECUTABLE) $< > profile.out
	vim profile.out
.PHONY: profile

gmon.out:
	-$(../build/fragments) 1787_query.lgf 2227.lgf
