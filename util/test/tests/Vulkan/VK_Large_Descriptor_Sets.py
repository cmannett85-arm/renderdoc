import renderdoc as rd
import os
import datetime
import rdtest


class VK_Large_Descriptor_Sets(rdtest.TestCase):
    demos_test_name = 'VK_Large_Descriptor_Sets'

    def run(self):
        self.capture_filename = self.get_capture()

        self.check(rdtest.util.path_exists(self.capture_filename), "Didn't generate capture in make_capture")

        rdtest.log.print("Loading capture")

        memory_before: int = rd.GetCurrentProcessMemoryUsage()
        start_time = self.get_time()

        self.controller = rdtest.open_capture(self.capture_filename, opts=self.get_replay_options())

        duration = self.get_time() - start_time
        memory_after: int = rd.GetCurrentProcessMemoryUsage()

        memory_increase = memory_after - memory_before

        rdtest.log.print("Loaded capture in {} seconds, consuming {} bytes of memory".format(duration, memory_increase))

        test_limit = 2000*1000*1000
        if not rdtest.util.get_remote_server() is None and \
            isinstance(rdtest.util.get_remote_server(), rdtest.remoteserver.AndroidRemoteServer):
            test_limit = 400*1000*1000

        if memory_increase > test_limit:
            raise rdtest.TestFailureException("Memory increase {} is too high".format(memory_increase))
        else:
            rdtest.log.success("Memory usage is OK")

        if rd.IsReleaseBuild():
            if duration.total_seconds() >= 2.5:
                raise rdtest.TestFailureException("Time to load is too high")
            rdtest.log.success("Time to load is OK")
        else:
            rdtest.log.print("Not checking time to load in non-release build")

        if self.controller is not None:
            self.controller.Shutdown()
