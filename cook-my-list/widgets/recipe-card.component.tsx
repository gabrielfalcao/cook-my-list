import React from "react";
import { GestureResponderEvent, StyleSheet } from "react-native";
import {
  Card,
  CardElement,
  CardProps,
  Text,
} from "@ui-kitten/components";
import { View } from "react-native";
import { TouchableHighlight } from "react-native";

import { ImageOverlay } from "./image-overlay.component";
import { Recipe } from "../types";
import { getRecipeImage } from "./food-images";
export interface RecipeCardProps extends Omit<CardProps, "children"> {
  recipe: Recipe;
  onPress?: (event: GestureResponderEvent) => void;
}

export type RecipeCardElement = React.ReactElement<RecipeCardProps>;

export const RecipeCard = (props: RecipeCardProps): CardElement => {
  const { style, recipe, onPress, ...cardProps } = props;

  return (
    <TouchableHighlight
      activeOpacity={0.6}
      underlayColor="#DDDDDD"
      onPress={() => {
        console.log(`RecipeCard onPress`, info);
        onPress();
      }}
    >
      <Card {...cardProps} style={[styles.container, style]}>
        <ImageOverlay style={styles.image} source={getRecipeImage(recipe)}>
          <Text style={styles.title} category="h6" status="control">
            {recipe.title}
          </Text>
          <View style={styles.layout}>
            {recipe.tags.map((tag) => {
              return (
                <View key={tag.name}>
                  <Text style={styles.tagName}>{tag.name}</Text>
                </View>
              );
            })}
          </View>
        </ImageOverlay>
      </Card>
    </TouchableHighlight>
  );
};

const styles = StyleSheet.create({
  container: {
    height: 200,
  },
  layout: {
    width: "100%",
    flex: 1,
    justifyContent: "flex-end",
    alignItems: "flex-start",
    flexWrap: "nowrap",
  },

  image: {
    ...StyleSheet.absoluteFillObject,
    height: 200,
    paddingVertical: 24,
    paddingHorizontal: 16,
  },
  level: {
    zIndex: 1,
  },
  tagName: {
    color: "#fff",
  },
  title: {
    zIndex: 1,
  },
  durationButton: {
    position: "absolute",
    left: 16,
    bottom: 16,
    borderRadius: 16,
    paddingHorizontal: 0,
  },
});

export default RecipeCard;
