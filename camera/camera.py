import cv2
import time

from ais.infrastructure.video import findUSBcameradevice


class VideoCam:
    '''
    Handles video streaming and frame capturing.
    '''
    def __init__(self, config: dict):
        # Load config
        self.config = config
        # Set capture device
        self._capture_device = self.config['camerausb']['capture_device']
        # if not defined, use find_camera_port
        if type(self._capture_device) is str:
            self._capture_device = findUSBcameradevice.find_camera_port(
                self._capture_device
            )
        self.capture = cv2.VideoCapture(
            self._capture_device,
            cv2.CAP_V4L2
        )

        if not self.capture.isOpened():
            raise Exception('Error: Could not open video source.')

        # Set MJPG format for highs resolutions
        self.capture.set(
            cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*'MJPG')
        )
        # Set the capture resolution to the maximum defined resolution
        self.capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.config['resolution'][0]
        )
        self.capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.config['resolution'][1]
        )

        # Store last frame
        self.frame = None

        # State variable, controls streamer while loop
        self.capture_ok = True

    def streamer(self):
        '''
        Generate frames for video streaming at a lower resolution.
        '''
        while self.capture_ok:
            ret, frame = self.capture.read()
            # Update flag based on capture status
            self.capture_ok = ret
            if ret:
                # Store the full-resolution frame
                self.frame = frame
                # Resize frame for streaming
                small_frame = cv2.resize(
                    frame,
                    self.config['streaming_resolution']
                )
                yield small_frame
                # Control max FPS on streaming
                time.sleep(1/self.config['stream']['max_fps'])

    def encoded_streamer(self):
        ''' Encoded frame streaming '''
        for frame in self.streamer():
            encoded_frame = self.encode_frame(frame)
            if encoded_frame:
                yield encoded_frame

    def encode_frame(self, frame):
        '''
        Returns binary representation of jpg encoded frame.
        Args:
        - frame (numpy.ndarray)
        '''
        encoded_frame = None
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            jpeg_bytes = jpeg.tobytes()
            encoded_frame = (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'
                + jpeg_bytes +
                b'\r\n'
            )
        return encoded_frame

    def capture_image(self):
        '''
        Save the latest frame in high resolution.
        '''
        last_frame = None
        if self.frame is not None:
            last_frame = self.frame
        return last_frame

    def release(self):
        '''
        Release camera.
        '''
        self.capture.release()
