# import paraview modules.
from paraview.web import pv_wslink
from paraview.web import protocols as pv_protocols

from paraview import simple
from wslink import server

import argparse

# =============================================================================
# Create custom PVServerProtocol class to handle clients requests
# =============================================================================


class _DemoServer(pv_wslink.PVServerProtocol):
    authKey = "wslink-secret"
    viewportScale = 1.0
    viewportMaxWidth = 2560
    viewportMaxHeight = 1440
    settingsLODThreshold = 102400

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            "--viewport-scale",
            default=1.0,
            type=float,
            help="Viewport scaling factor",
            dest="viewportScale",
        )
        parser.add_argument(
            "--viewport-max-width",
            default=2560,
            type=int,
            help="Viewport maximum size in width",
            dest="viewportMaxWidth",
        )
        parser.add_argument(
            "--viewport-max-height",
            default=1440,
            type=int,
            help="Viewport maximum size in height",
            dest="viewportMaxHeight",
        )
        parser.add_argument(
            "--settings-lod-threshold",
            default=102400,
            type=int,
            help="LOD Threshold in Megabytes",
            dest="settingsLODThreshold",
        )

    @staticmethod
    def configure(args):
        # Update this server based on the passed in arguments
        _DemoServer.authKey = args.authKey
        _DemoServer.viewportScale = args.viewportScale
        _DemoServer.viewportMaxWidth = args.viewportMaxWidth
        _DemoServer.viewportMaxHeight = args.viewportMaxHeight
        _DemoServer.settingsLODThreshold = args.settingsLODThreshold

    def initialize(self):
        # Bring used components
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebMouseHandler())
        self.registerVtkWebProtocol(pv_protocols.ParaViewWebViewPort())
        self.registerVtkWebProtocol(
            pv_protocols.ParaViewWebPublishImageDelivery(decode=False)
        )
        self.updateSecret(_DemoServer.authKey)

        # tell the C++ web app to use no encoding.
        # ParaViewWebPublishImageDelivery must be set to decode=False to match.
        self.getApplication().SetImageEncoding(0)

        # Disable interactor-based render calls
        simple.GetRenderView().EnableRenderOnInteraction = 0
        simple.GetRenderView().Background = [0, 0, 0]
        cone = simple.Cone()
        simple.Show(cone)
        simple.Render()

        # Update interaction mode
        pxm = simple.servermanager.ProxyManager()
        interactionProxy = pxm.GetProxy("settings", "RenderViewInteractionSettings")
        interactionProxy.Camera3DManipulators = [
            "Rotate",
            "Pan",
            "Zoom",
            "Pan",
            "Roll",
            "Pan",
            "Zoom",
            "Rotate",
            "Zoom",
        ]


# =============================================================================
# Main: Parse args and start server
# =============================================================================


if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="ParaViewWeb Demo")

    # Add default arguments
    server.add_arguments(parser)
    _DemoServer.add_arguments(parser)

    # Extract arguments
    args = parser.parse_args()
    _DemoServer.configure(args)

    # Start server
    server.start_webserver(options=args, protocol=_DemoServer)
