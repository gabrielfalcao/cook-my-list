import React from "react";
import { StyleSheet } from "react-native";
import {
  Button,
  Card,
  CardElement,
  CardProps,
  Text,
} from "@ui-kitten/components";
import { ImageOverlay } from "./image-overlay.component";
import { Recipe } from "./types";
import { getRecipeImage } from "./food-images";
export interface RecipeCardProps extends Omit<CardProps, "children"> {
  recipe: Recipe;
}

export type RecipeCardElement = React.ReactElement<RecipeCardProps>;

export const RecipeCard = (props: RecipeCardProps): CardElement => {
  const { style, recipe, ...cardProps } = props;

  return (
    <Card {...cardProps} style={[styles.container, style]}>
      <ImageOverlay
        style={styles.image}
        source={getRecipeImage(recipe.imageName)}
      >
        <Text style={styles.title} category="h6" status="control">
          {recipe.title}
        </Text>
      </ImageOverlay>
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    height: 200,
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
