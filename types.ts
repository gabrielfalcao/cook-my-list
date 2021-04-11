
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
