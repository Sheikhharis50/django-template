cd $server

echo "Pulling new changes..."
git pull

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running migrations..."
./scripts/migrate_and_seed.sh

echo "Restarting server..."
sudo supervisorctl reload