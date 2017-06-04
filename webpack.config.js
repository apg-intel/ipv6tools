var path = require('path')
var webpack = require('webpack')

module.exports = {
  // entry point of our application
  entry: './client/main.js',
  // where to place the compiled bundle
  output: {
    path: path.join(__dirname, 'assets'),
    publicPath: "/assets/",
    filename: 'app.js'
  },
  devServer: {
    proxy: {
      '/socket.io': 'http://localhost:8080'
    },
    disableHostCheck: true
  },
  /* resolveLoader: {
    root: path.join(__dirname, 'node_modules'),
  }, */
  module: {
    // `loaders` is an array of loaders to use.
    // here we are only configuring vue-loader
    loaders: [
      {
        test: /\.woff(\?v=\d+\.\d+\.\d+)?$/,
        loader: "url-loader?limit=10000&mimetype=application/font-woff"
      }, 
      {
        test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/,
        loader: "url-loader?limit=10000&mimetype=application/font-woff"
      }, 
      {
        test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
        loader: "url-loader?limit=10000&mimetype=application/octet-stream"
      }, 
      {
        test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
        loader: "file-loader"
      }, 
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        loader: "url-loader?limit=10000&mimetype=image/svg+xml"
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        loader: "style-loader!css-loader"
      }
    ],
  },
  plugins: [
    new webpack.optimize.UglifyJsPlugin({
      compress: {
        warnings: false
      }
    }),
    new webpack.ProvidePlugin({
      'utils': 'utils'
    })
  ],
  resolve: {
    alias: {
      vue: 'vue/dist/vue.common.js',
      utils: path.resolve(__dirname, './client/utils')
    }
  },
}
