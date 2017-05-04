/**
 * Created by Nitori on 2017/5/1.
 */
import path from 'path';
import webpack from 'webpack';
import ExtractTextPlugin from 'extract-text-webpack-plugin';
import autoprefixer from 'autoprefixer';

const extractCSS = new ExtractTextPlugin({ filename: 'coupon.css', allChunks: true });

function babelLoader() {
    return {
        loader: 'babel-loader',
        options: {
            ...require(path.resolve(__dirname, 'package.json')).babelForProject,
        }
    };
}


export default function (env = {}) {
    const config = {
        bail: true,
        context: path.resolve(__dirname, 'coupon', 'ui'),
        devtool: env.production ? 'source-map' : false,
        entry: {
            bootstrap: 'bootstrap-loader',
            coupon: path.resolve(__dirname, 'coupon', 'ui', 'Entry.js'),
        },
        output: {
            path: path.resolve(__dirname, 'coupon', '.static'),
            publicPath: '/',
            hashFunction: 'sha1',
            hashDigest: 'hex',
            hashDigestLength: 10,
            filename: '[name].js?[chunkhash]',
            chunkFilename: '[name].chunk.js?[chunkhash]',
        },
        resolve: {
            modules: [
                path.resolve(__dirname, 'node_modules'),
            ],
        },
        module: {
            rules: [
                {
                    test: /\.js$/,
                    exclude: /node_modules[\/\\]/,
                    use: [babelLoader()],
                },
                {
                    test: /\.css$/,
                    include: /node_modules[\/\\]/,
                    use: extractCSS.extract(
                        ['css-loader?importLoaders=1', 'postcss-loader'],
                    )
                },
                {
                    test: /\.scss$/,
                    include: /node_modules[\/\\]/,
                    use: extractCSS.extract(
                        ['css-loader?importLoaders=1', 'postcss-loader', 'sass-loader'],
                    )
                },

                {
                    test: /\.woff2?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                    // Limiting the size of the woff fonts breaks font-awesome ONLY for the extract text plugin
                    // use: "url?limit=10000"
                    use: 'file-loader',
                },
                {
                    test: /\.(ttf|eot|svg)(\?[\s\S]+)?$/,
                    use: 'file-loader',
                },

                // Use one of these to serve jQuery for Bootstrap scripts:

                // Bootstrap 4
                { test: /bootstrap\/dist\/js\/umd\//, use: 'imports-loader?jQuery=jquery' },
            ],
        },
        plugins: [
            new webpack.ProvidePlugin({
                $: 'jquery',
                jQuery: 'jquery',
                'window.jQuery': 'jquery',
                tether: 'tether',
                Tether: 'tether',
                'window.Tether': 'tether',
            }),
            extractCSS,
            env.production
                ? new webpack.optimize.UglifyJsPlugin({ sourceMap: false })
                : function () {},
            new webpack.LoaderOptionsPlugin({
                options: {
                    context: __dirname,
                    postcss: [require('autoprefixer')],
                },
            }),
        ],
    };
    return config;
}