import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
import numpy as np

def train_recommendation_model(user_embeddings, product_embeddings, review_data):
    # Prepare training data
    X = []
    y = []
    for _, row in review_data.iterrows():
        user_emb = user_embeddings[row['user_id']]
        product_emb = product_embeddings[row['product_id']]
        X.append(np.concatenate([user_emb, product_emb]))
        y.append(row['rating'])

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32)

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Convert data to PyTorch tensors
    X_train = torch.tensor(X_train)
    y_train = torch.tensor(y_train).unsqueeze(1)  # Add an extra dimension for compatibility
    X_test = torch.tensor(X_test)
    y_test = torch.tensor(y_test).unsqueeze(1)

    # Check if GPU is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Move data to GPU if available
    X_train, y_train = X_train.to(device), y_train.to(device)
    X_test, y_test = X_test.to(device), y_test.to(device)

    # Define the model
    class RecommendationModel(nn.Module):
        def __init__(self):
            super(RecommendationModel, self).__init__()
            self.fc1 = nn.Linear(X_train.shape[1], 128)
            self.fc2 = nn.Linear(128, 64)
            self.fc3 = nn.Linear(64, 1)

        def forward(self, x):
            x = torch.relu(self.fc1(x))
            x = torch.relu(self.fc2(x))
            x = self.fc3(x)
            return x

    model = RecommendationModel().to(device)

    # Define loss function and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    epochs = 10
    batch_size = 32
    for epoch in range(epochs):
        model.train()
        permutation = torch.randperm(X_train.size(0))
        for i in range(0, X_train.size(0), batch_size):
            indices = permutation[i:i + batch_size]
            batch_X, batch_y = X_train[indices], y_train[indices]

            # Zero the gradients
            optimizer.zero_grad()

            # Forward pass
            outputs = model(batch_X)

            # Compute loss
            loss = criterion(outputs, batch_y)

            # Backward pass and optimization
            loss.backward()
            optimizer.step()

        # Validation
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_test)
            val_loss = criterion(val_outputs, y_test)
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss.item()}, Validation Loss: {val_loss.item()}")

    return model