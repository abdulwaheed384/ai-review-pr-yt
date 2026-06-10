terraform {

  cloud {

    organization = "ai-tf-yt-org"

    workspaces {
      name = "ai-pr-review-dev"
    }

  }

}

provider "azurerm" {
  features {}
}