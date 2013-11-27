                        var username = "{{ user.username }}";
                        var tour = {
                          id: "lianpeng_tour",
                          fixedElement: true,
                          steps: [
                            {
                              title: "点击右侧“添加链接”按钮，收藏你在莲蓬的第一个网页",
                                     content: "在出现的表单里，点击<span class='label label-success'>保存</span>按钮即完成。",
                              target: ".add-bookmark-form .btn-add-bookmark",
                              //showNextButton: false,
                              //nextOnTargetClick: true,
                              multipage: true,
                              placement: "left",
                              onNext: function() {
                                  window.location = "/tools/";
                              },
                            },
                            {
                              title: "点击上方的按钮安装收藏工具",
                              content: "在浏览网页的时候，使用收藏工具一键收藏，不用登录到莲蓬主站也可以收藏。",
                              target: "#chrome-bookmarklet-box a",
                              multipage: true,
                              onNext: function() {
                                  window.location = "/import/";
                              },
                              showPrevButton: true,
                              placement: "bottom"
                            },
                            {
                              title: "导入现有的书签",
                              content: "如果之前已经使用其他书签收藏服务，例如Delicious/Google书签，或者是浏览器的书签，你可以将之导出并导入到莲蓬。",
                              target: "#id_site",
                              multipage: true,
                              onNext: function() {
                                  window.location = "/" + username + "/inbox/";
                              },
                              showPrevButton: true,
                              placement: "bottom"
                            },
                            {
                              title: "创建专辑",
                              content: "可以对收藏的网页进行整理分类，形成一个专辑，例如：电影，Web开发，创业等。",
                              target: ".new-list-button",
                              showPrevButton: true,
                              placement: "bottom"
                            },
                            {
                              title: "分享专辑",
                              content: "对于专辑，你可以将它公开使得大家都可以看到专辑里的收藏，也可以邀请好友、同事私享你的专辑。",
                              target: ".list-setting-box .btn",
                              showPrevButton: true,
                              placement: "left"
                            },
                            {
                              title: "搜索",
                              content: "在慢慢积累了很多网页后，没法一页一页很快找到，通过关键字对以前的收藏进行检索将会非常方便。",
                              target: ".search .query",
                              showPrevButton: true,
                              placement: "bottom"
                            },
                          ]
                        };

