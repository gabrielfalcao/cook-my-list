import React from "react";
import {
  GestureResponderEvent,
  ImageBackground,
  ImageBackgroundProps,
  StyleProp,
  StyleSheet,
  View,
  ViewStyle,
} from "react-native";

interface OverlayImageStyle extends ViewStyle {
  overlayColor?: string;
}

export interface ImageOverlayProps extends ImageBackgroundProps {
  style?: StyleProp<OverlayImageStyle>;
  children?: React.ReactNode;
  onPress?: (event: GestureResponderEvent) => void;
}

const DEFAULT_OVERLAY_COLOR = "rgba(0, 0, 0, 0.45)";

export const ImageOverlay = (
  props?: ImageOverlayProps
): React.ReactElement<ImageBackgroundProps> => {
  const { style, children, onPress, ...imageBackgroundProps } = props;
  const { overlayColor, ...imageBackgroundStyle } = StyleSheet.flatten(style);

  return (
    <ImageBackground {...imageBackgroundProps} style={imageBackgroundStyle}>
      <View
        style={[
          StyleSheet.absoluteFill,
          { backgroundColor: overlayColor || DEFAULT_OVERLAY_COLOR },
        ]}
      />
      {children}
    </ImageBackground>
  );
};
