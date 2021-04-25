export type RecipeDetailsParams = { recipeId : string}
export type RootStackParamList = {
    Home: undefined;
    Logout: undefined;
    RecipeDetails: RecipeDetailsParams;
    Profile: { userId: string };
    Feed: { sort: 'latest' | 'top' } | undefined;
};

export interface Ingredient {
    name: string,
    imageName: string,
}

export interface Recipe {
    title: string,
    imageName: string,
    tags: RecipeTag[]
}

export interface RecipeTag {
    name: string,
    iconName: string,
}
