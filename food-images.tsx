import egg from "cook-my-list/assets/food-icons/egg.jpg";
import broccoli from "cook-my-list/assets/food-icons/broccoli.jpg";
import cheese from "cook-my-list/assets/food-icons/cheese.jpg";
import shrimp from "cook-my-list/assets/food-icons/shrimp.jpg";

import empanadaoCamaraoLegumes from "cook-my-list/assets/recipe-images/empanadao-camarao-legumes.jpg";
import souffleDeBroccoli from "cook-my-list/assets/recipe-images/souffle-de-brocoli.jpg";
import brocolisComOvo from "cook-my-list/assets/recipe-images/brocolis-com-ovo.jpg";

import lowCarbIcon from "cook-my-list/assets/icons/avocado.svg";
import portionIcon from "cook-my-list/assets/icons/portion.svg";
import timerIcon from "cook-my-list/assets/icons/timer.svg";
import { RecipeTag, Ingredient, Recipe } from "cook-my-list/types";

const knownIngredients = { egg, broccoli, cheese, shrimp };

const knownRecipes = {
  "empanadao-camarao-legumes": empanadaoCamaraoLegumes,
  "souffle-de-brocoli": souffleDeBroccoli,
  "brocolis-com-ovo": brocolisComOvo,
};

const knownTags = {
  "low-carb": lowCarbIcon,
  portion: portionIcon,
  timer: timerIcon,
};

export function getIngredientImage(ingredient: Ingredient): any {
  return knownIngredients[ingredient.imageName];
}

export function getRecipeImage(recipe: Recipe): any {
  return knownRecipes[recipe.imageName];
}

export function getTagImage(tag: RecipeTag): any {
  return knownTags[tag.iconName];
}
export default { ...knownIngredients, ...knownRecipes };
