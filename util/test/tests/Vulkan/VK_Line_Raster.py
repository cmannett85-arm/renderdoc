import rdtest
import renderdoc as rd


class VK_Line_Raster(rdtest.TestCase):
    demos_test_name = 'VK_Line_Raster'

    def _configure_points(self):
        texdetails = self.get_texture(self.tex)

        # Each viewport takes up 25% of the viewport dimensions
        self.view = [int(texdetails.width * 0.25), int(texdetails.height * 0.25)]

        # Each line starts and end at the viewport's corner offset by 5% of the viewport dimensions
        # per end (plus a raster fudge factor)
        self.points = [
            [int(self.view[0] * 0.05) + 2, int(self.view[1] * 0.95) - 2],
            [int(self.view[0] * 0.5), int(self.view[1] * 0.5)],
            [int(self.view[0] * 0.95) - 2, int(self.view[1] * 0.05) + 2],
        ]


    def sample(self, row, col):
        ret = []
        for p in self.points:
            x = self.view[0] * col + p[0]
            y = self.view[1] * row + p[1]

            picked: rd.PixelValue = self.controller.PickPixel(self.tex, x, y, rd.Subresource(0, 0, 0), rd.CompType.Typeless)
            ret.append(rdtest.value_compare(picked.floatValue, [0.0, 1.0, 1.0, 1.0]))
        return ret

    def check_capture(self):
        action = self.find_action("vkCmdEndRenderPass")

        self.check(action is not None)

        action = action.previous

        self.controller.SetFrameEvent(action.eventId, False)

        pipe: rd.PipeState = self.controller.GetPipelineState()

        self.tex = pipe.GetOutputTargets()[0].resource
        self._configure_points()

        # Top left we expect a regular line segment.
        s = self.sample(0, 0)

        # All points should be the line color
        if not rdtest.value_compare(s, [True, True, True]):
            raise rdtest.TestFailureException("Normal line picked values {} doesn't match expectation".format(s))

        # Next row is unstippled. The lines should either be all present, or not present
        names = ["Rectangle", "Bresenham", "Rectangle Round"]
        for col in [0, 1, 2]:
            s = self.sample(1, col)

            n = "Unstippled {}".format(names[col])

            if s[0]:
                if not rdtest.value_compare(s, [True, True, True]):
                    raise rdtest.TestFailureException("{} picked values {} doesn't match expectation".format(n, s))
                rdtest.log.success("{} line looks as expected".format(n))
            else:
                if not rdtest.value_compare(s, [False, False, False]):
                    raise rdtest.TestFailureException("{} picked values {} doesn't match expectation".format(n, s))
                rdtest.log.success("{} line not supported".format(n))

        # Final row is stippled. The lines should be present on each end, and not present in the middle
        # (or not present at all)
        for col in [0, 1, 2]:
            s = self.sample(2, col)

            n = "Stippled {}".format(names[col])

            if s[0]:
                if not rdtest.value_compare(s, [True, False, True]):
                    raise rdtest.TestFailureException("{} picked values {} doesn't match expectation".format(n, s))
                rdtest.log.success("{} line looks as expected".format(n))
            else:
                if not rdtest.value_compare(s, [False, False, False]):
                    raise rdtest.TestFailureException("{} picked values {} doesn't match expectation".format(n, s))
                rdtest.log.success("{} line not supported".format(n))

        rdtest.log.success("All lines look as expected")
