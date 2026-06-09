terraform {

  cloud {

    organization = "ai-tf-yt-org"

    workspaces {
      name = "ai-pr-review-dev"
    }

  }

  required_providers {

    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }

  }
}

provider "azurerm" {
  features {}
}