import re
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from backend.config.deployments import ModelDeploymentName


def test_list_deployments(
    client: TestClient, mock_available_model_deployments: Mock
) -> None:
    response = client.get("/deployments")
    assert response.status_code == 200
    deployments = response.json()
    assert len(deployments) == 2
    for deployment in deployments:
        assert "name" in deployment
        assert "models" in deployment
        assert "env_vars" in deployment

    assert deployments[0]["env_vars"] == ["COHERE_VAR_1", "COHERE_VAR_2"]
    assert deployments[1]["env_vars"] == ["SAGEMAKER_VAR_1", "SAGEMAKER_VAR_2"]


@pytest.mark.parametrize(
    "mock_available_model_deployments",
    [{ModelDeploymentName.SageMaker: False}],
    indirect=True,
)
def test_list_deployments_only_shows_available_models_by_default(
    client: TestClient, mock_available_model_deployments
) -> None:
    response = client.get("/deployments")
    assert response.status_code == 200
    deployments = response.json()
    assert len(deployments) == 1
    assert deployments[0]["name"] == ModelDeploymentName.CoherePlatform
    assert deployments[0]["models"] == ["test"]


@pytest.mark.parametrize(
    "mock_available_model_deployments",
    [{ModelDeploymentName.SageMaker: False}],
    indirect=True,
)
def test_list_deployments_has_all_option(
    client: TestClient, mock_available_model_deployments
) -> None:
    response = client.get("/deployments?all=1")
    assert response.status_code == 200
    deployments = response.json()
    assert len(deployments) == len(list(ModelDeploymentName))


@pytest.mark.parametrize(
    "mock_available_model_deployments",
    [{model: False for model in list(ModelDeploymentName)}],
    indirect=True,
)
def test_list_deployments_no_available_models_404(
    client: TestClient, mock_available_model_deployments: Mock
) -> None:
    response = client.get("/deployments")
    assert response.status_code == 404
    assert response.json() == {
        "detail": [
            (
                "No available deployments found. Please ensure that the required environment variables are set up correctly. "
                "Refer to the README.md for detailed instructions."
            )
        ]
    }


@pytest.mark.parametrize(
    "mock_available_model_deployments",
    [{model: False for model in list(ModelDeploymentName)}],
    indirect=True,
)
def test_list_deployments_no_available_models_with_all_option(
    client: TestClient, mock_available_model_deployments: Mock
) -> None:
    response = client.get("/deployments?all=1")
    assert response.status_code == 200
    assert len(response.json()) == len(list(ModelDeploymentName))


def test_set_env_vars(
    client: TestClient, mock_available_model_deployments: Mock
) -> None:
    with patch("backend.services.env.set_key") as mock_set_key:
        response = client.post(
            "/deployments/Cohere+Platform/set_env_vars",
            json={
                "env_vars": {
                    "COHERE_VAR_1": "TestCohereValue",
                },
            },
        )
    assert response.status_code == 200

    class EnvPathMatcher:
        def __eq__(self, other):
            return bool(re.match(r".*/?\.env$", other))

    mock_set_key.assert_called_with(
        EnvPathMatcher(),
        "COHERE_VAR_1",
        "TestCohereValue",
    )


def test_set_env_vars_with_invalid_deployment_name(
    client: TestClient, mock_available_model_deployments: Mock
):
    response = client.post("/deployments/unknown/set_env_vars", json={})
    assert response.status_code == 404


def test_set_env_vars_with_var_for_other_deployment(
    client: TestClient, mock_available_model_deployments: Mock
) -> None:
    response = client.post(
        "/deployments/Cohere+Platform/set_env_vars",
        json={
            "env_vars": {
                "SAGEMAKER_VAR_1": "TestSageMakerValue",
            },
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Environment variables not valid for deployment: SAGEMAKER_VAR_1"
    }


def test_set_env_vars_with_invalid_var(
    client: TestClient, mock_available_model_deployments: Mock
) -> None:
    response = client.post(
        "/deployments/Cohere+Platform/set_env_vars",
        json={
            "env_vars": {
                "API_KEY": "12345",
            },
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Environment variables not valid for deployment: API_KEY"
    }
