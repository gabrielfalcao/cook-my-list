import { Ingredient, Recipe } from "./types";

export const ingredients: Ingredient[] = [
  { name: "Ovo", imageName: "egg" },
  { name: "Queijo", imageName: "cheese" },
  { name: "Brócolis", imageName: "broccoli" },
  { name: "Camarão", imageName: "shrimp" },
];

export const recipes: Recipe[] = [
  {
    title: "Empanadão de camarão com legumes",
    imageName: "empanadao-camarao-legumes",
    tags: [
      {
        name: "40 min",
        iconName: "",
      },
      {
        name: "8 porções",
        iconName: "portion",
      },
    ],
  },
  {
    title: "Souflé de Brócolis",
    imageName: "souffle-de-brocoli",
    tags: [
      {
        name: "30 min",
        iconName: "timer",
      },
      {
        name: "6 porções",
        iconName: "portion",
      },
      {
        name: "Low Carb",
        iconName: "low-carb",
      },
    ],
  },
  {
    title: "Brócolis com Ovo",
    imageName: "brocolis-com-ovo",
    tags: [
      {
        name: "40 min",
        iconName: "timer",
      },
      {
        name: "6 porções",
        iconName: "portion",
      },
    ],
  },
];
