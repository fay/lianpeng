                        var tour = {
                          id: "lianpeng_tour",
                          fixedElement: true,
                          steps: [
                            {
                              title: "点击右侧“添加链接”按钮，收藏你在莲蓬的第一个网页",
                                     content: "在出现的表单里，点击<span class='label label-success'>保存</span>按钮即完成。",
                              target: ".add-bookmark-form .btn-add-bookmark",
                              //showNextButton: false,
                              placement: "left"
                            },
                            {
                              title: "安装收藏工具",
                              content: "在浏览网页的时候，使用收藏工具一键收藏，不用登录到莲蓬主站也可以收藏。",
                              target: ".tool-menu a i",
                              multipage: true,
                              onNext: function() {
                                  window.location = "/tools/"
                              },
                              nextOnTargetClick: true,
                              showPrevButton: true,
                              placement: "bottom"
                            },
                            {
                              title: "点击上方的按钮安装收藏工具",
                              content: "在浏览网页的时候，使用收藏工具一键收藏，不用登录到莲蓬主站也可以收藏。",
                              target: "#chrome-bookmarklet-box a",
                              multipage: true,
                              onNext: function() {
                                  window.location = "/tools/"
                              },
                              nextOnTargetClick: true,
                              showPrevButton: true,
                              placement: "bottom"
                            },
                            {
                              title: "导入现有的书签",
                              content: "如果之前已经使用其他书签收藏服务，例如Delicious/Google书签，或者是浏览器的书签，你可以将之导出并导入到莲蓬。",
                              target: ".import-menu",
                              multipage: true,
                              onNext: function() {
                                  window.location = "/tools/"
                              },
                              nextOnTargetClick: true,
                              showPrevButton: true,
                              placement: "bottom"
                            }
                          ]
                        };

