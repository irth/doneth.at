yarn
yarn install
yarn build
source .envrc
flask digest clean
flask db upgrade
flask run
