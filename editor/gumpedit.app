<app:application help="./Readme.html" home="~/"
     name="Gump Descriptor Editor" splash="./gump.gif"
     xmlns:app="http://www.jbrix.org/ApplicationSchema"
     xmlns:xforms="http://www.jbrix.org/FormSchema"
     xmlns:xplus="http://www.jbrix.org/XMLUtilitySchema">
    <xplus:cache echo="off" key="{@name}" name="xforms" scope="app"
         target="xforms:form"/>
    <tips>
        <tip>For more information about the Gump system, look at the Gump site: &lt;a href=&quot;http://jakarta.apache.org/gump&quot;&gt;http://jakarta.apache.org/gump &lt;/a&gt;.</tip>
    </tips>
    <app:type editor="gumpedit" extensions="xml" id="gumpedit" tag="module"/>
    <app:editor class="org.jbrix.gui.app.XPad" id="gumpedit"
         window.title="%f - Gumpedit - Gump descriptor editor">
        <form ref="">
            <components>
                <textfield ref="@name">
                    <caption>name</caption>
                </textfield>
                <separator>
                    <caption>(New Field)</caption>
                </separator>
                <zoombutton button.key="site, code, community" ref=".">
                    <caption>resources</caption>
                    <form>
                        <caption>Resources</caption>
                        <components>
                            <zoombutton button.key="website" ref=".">
                                <caption>website</caption>
                                <form>
                                    <caption>Website</caption>
                                    <components>
                                        <textfield ref="url/@href">
                                            <caption>public url</caption>
                                        </textfield>
                                        <textfield ref="site/@hostname">
                                            <caption>hostname</caption>
                                        </textfield>
                                        <textfield ref="site/@remotedir">
                                            <caption>remore dir</caption>
                                        </textfield>
                                    </components>
                                </form>
                            </zoombutton>
                            <zoombutton button.key="code repository" ref="cvs">
                                <caption>code repository</caption>
                                <form>
                                    <caption>Code repository</caption>
                                    <components>
                                        <textfield ref="@repository">
                                            <caption>repository</caption>
                                        </textfield>
                                        <textfield ref="@host-prefix">
                                            <caption>host prefix</caption>
                                        </textfield>
                                        <textfield ref="@dir">
                                            <caption>dir</caption>
                                        </textfield>
                                        <textfield ref="@module">
                                            <caption>module</caption>
                                        </textfield>
                                        <textfield ref="@href">
                                            <caption>web nav url</caption>
                                        </textfield>
                                    </components>
                                </form>
                            </zoombutton>
                            <textfield ref="bugtrack/@href">
                                <caption>bugtrack</caption>
                            </textfield>
                            <table ref="mailing-lists/mailing-list">
                                <caption>mailing lists</caption>
                                <column name="user" ref="@user" width="181"/>
                                <column name="mail" ref="@mail" width="181"/>
                                <form>
                                    <caption>Mailing list  {@name}</caption>
                                    <components>
                                        <textfield ref="@user">
                                            <caption>user</caption>
                                        </textfield>
                                        <textfield ref="@mail">
                                            <caption>address</caption>
                                        </textfield>
                                        <textfield ref="@subscribe">
                                            <caption>subscribe</caption>
                                        </textfield>
                                        <textfield ref="@unsubscribe">
                                            <caption>unsubscribe</caption>
                                        </textfield>
                                        <table ref="archives/archive">
                                            <caption>archives</caption>
                                            <column name="name" ref="@name"
                                                 width="63"/>
                                            <column name="href" ref="@href"
                                                 width="305"/>
                                            <form>
                                                <caption>Archive</caption>
                                                <components>
                                                    <textfield ref="@name">
                                                        <caption>name</caption>
                                                    </textfield>
                                                    <textfield ref="@href">
                                                        <caption>href</caption>
                                                    </textfield>
                                                </components>
                                            </form>
                                        </table>
                                    </components>
                                </form>
                            </table>
                        </components>
                    </form>
                </zoombutton>
                <textfield ref="description">
                    <caption>description</caption>
                </textfield>
                <textarea ref="detailed">
                    <caption>detailed description</caption>
                </textarea>
                <textarea ref="why">
                    <caption>itch</caption>
                </textarea>
                <table ref="what/goal">
                    <caption>goals</caption>
                    <form>
                        <caption>New Form</caption>
                        <components>
                            <textarea ref=".">
                                <caption>Goal</caption>
                            </textarea>
                        </components>
                    </form>
                    <column name="goal" ref="."/>
                </table>
                <separator>
                    <caption>(New Field)</caption>
                </separator>
                <table ref="project">
                    <caption>projects</caption>
                    <column name="name" ref="@name"/>
                    <form>
                        <caption>Project {@name}</caption>
                        <components>
                            <textfield ref="@name">
                                <caption>name</caption>
                            </textfield>
                            <zoombutton
                                 button.key=" {@major}-{@minor}-{@fix}-{@tag}"
                                 ref="version">
                                <caption>version</caption>
                                <form>
                                    <caption>Version</caption>
                                    <components>
                                        <textfield ref="@major">
                                            <caption>major</caption>
                                        </textfield>
                                        <textfield ref="@minor">
                                            <caption>minor</caption>
                                        </textfield>
                                        <textfield ref="@fix">
                                            <caption>bugfix</caption>
                                        </textfield>
                                        <textfield ref="@tag">
                                            <caption>tag</caption>
                                        </textfield>
                                    </components>
                                </form>
                            </zoombutton>
                            <textfield ref="package">
                                <caption>package</caption>
                            </textfield>
                            <zoombutton button.key="build" ref=".">
                                <caption/>
                                <form>
                                    <caption>Build</caption>
                                    <components>
                                        <textfield ref="ant/@target">
                                            <caption>ant target</caption>
                                        </textfield>
                                        <textfield ref="ant/@vm">
                                            <caption>ant vm</caption>
                                        </textfield>
                                        <textfield ref="build/@script">
                                            <caption>build script</caption>
                                        </textfield>
                                    </components>
                                </form>
                            </zoombutton>
                            <zoombutton button.key="dependencies" ref=".">
                                <caption/>
                                <form>
                                    <caption>Dependencies</caption>
                                    <components>
                                        <table ref="depend">
                                            <caption>core</caption>
                                            <column name="project"
                                                 ref="@project"/>
                                            <form>
                                                <caption>core</caption>
                                                <components>
                                                    <textfield ref="@project">
                                                        <caption>project dependency</caption>
                                                    </textfield>
                                                </components>
                                            </form>
                                        </table>
                                        <table ref="optional">
                                            <caption>optional</caption>
                                            <column name="project"
                                                 ref="@project"/>
                                            <form>
                                                <caption>optional</caption>
                                                <components>
                                                    <textfield ref="@project">
                                                        <caption>optional project</caption>
                                                    </textfield>
                                                </components>
                                            </form>
                                        </table>
                                    </components>
                                </form>
                            </zoombutton>
                            <zoombutton button.key="work and result dirs"
                                 ref=".">
                                <caption/>
                                <form>
                                    <caption>Dirs</caption>
                                    <components>
                                        <table ref="work">
                                            <caption>work</caption>
                                            <column name="dir" ref="@nested"/>
                                            <form ref="">
                                                <caption>work</caption>
                                                <components>
                                                    <textfield ref="@nested">
                                                        <caption>work dir</caption>
                                                    </textfield>
                                                </components>
                                            </form>
                                        </table>
                                        <textfield ref="home/@nested">
                                            <caption>home dir</caption>
                                        </textfield>
                                    </components>
                                </form>
                            </zoombutton>
                        </components>
                    </form>
                </table>
            </components>
            <caption>Module {@name}</caption>
        </form>
    </app:editor>
</app:application>